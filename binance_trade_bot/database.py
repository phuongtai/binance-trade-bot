import json
import os
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Optional, Union
import pymongo

from socketio import Client
from socketio.exceptions import ConnectionError as SocketIOConnectionError
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from mongoengine import connect, register_connection, disconnect

from .config import Config
from .logger import Logger
from .models import *  # pylint: disable=wildcard-import


class Database:
    def __init__(self, logger: Logger, config: Config, uri="sqlite:///data/crypto_trading.db"):
        self.logger = logger
        self.config = config
        # self.client_db = connect((host=))
        # self.engine = create_engine(uri)
        # self.SessionMaker = sessionmaker(bind=self.engine)
        self.socketio_client = Client()
        print(self.config.MONGO_DB_URI)
        connect('crypto_trading', host=self.config.MONGO_DB_URI)

    def destroy_session(self):
        disconnect()

    def socketio_connect(self):
        if self.socketio_client.connected and self.socketio_client.namespaces:
            return True
        try:
            if not self.socketio_client.connected:
                self.socketio_client.connect("http://api:5123", namespaces=["/backend"])
            while not self.socketio_client.connected or not self.socketio_client.namespaces:
                time.sleep(0.1)
            return True
        except SocketIOConnectionError:
            return False

    @contextmanager
    def db_session(self):
        """
        Creates a context with an open SQLAlchemy session.
        """
        

    def set_coins(self, symbols: List[str]):

        # For all the coins in the database, if the symbol no longer appears
        # in the config file, set the coin as disabled
        coins: List[Coin] = Coin.objects
        for coin in coins:
            if coin.symbol not in symbols:
                coin.enabled = False

        # For all the symbols in the config file, add them to the database
        # if they don't exist
        for symbol in symbols:
            coin = next((coin for coin in coins if coin.symbol == symbol), None)
            if coin is None:
                coin_db = Coin(symbol=symbol)
                coin_db.save()
            else:
                coin.enabled = True

        # For all the combinations of coins in the database, add a pair to the database
        coins: Coin.objects
        for from_coin in coins:
            for to_coin in coins:
                if from_coin != to_coin:
                    pair = Pair.objects(from_coin =from_coin, to_coin=to_coin).first()
                    if pair is None:
                        pair = Pair(from_coin=from_coin, to_coin=from_coin)
                        pair.save()

    def get_coins(self, only_enabled=True) -> List[Coin]:
        if only_enabled:
            coins = Coin.objects(enabled=True).all()
        else:
            coins = Coin.objects
        return coins

    def get_coin(self, coin: Union[Coin, str]) -> Coin:
        if isinstance(coin, Coin):
            return coin
        coin = Coin.objects(symbol=coin).first()
        return coin

    def set_current_coin(self, coin: Union[Coin, str]):
        coin = self.get_coin(coin)
        current_coin = CurrentCoin(coin=coin)
        current_coin.save()

    def get_current_coin(self) -> Optional[Coin]:
        current_coin = CurrentCoin.objects.order_by('-datetime').first()
        if current_coin is None:
            return None
        coin = current_coin.coin
        return coin

    def get_pair(self, from_coin: Union[Coin, str], to_coin: Union[Coin, str]):
        from_coin = self.get_coin(from_coin)
        to_coin = self.get_coin(to_coin)
        pair: Pair.objects(from_coin=from_coin, to_coin = to_coin).first()
        return pair

    def get_pairs_from(self, from_coin: Union[Coin, str], only_enabled=True) -> List[Pair]:
        from_coin = self.get_coin(from_coin)

        pairs = Pair.objects(from_coin=from_coin)
        if only_enabled:
            pairs = pairs.filter(enabled=True)
        pairs = pairs.all()
        return pairs


    def get_pairs(self, only_enabled=True) -> List[Pair]:
        pairs = Pair.objects
        if only_enabled:
            pairs = pairs.filter(enabled=True)
        pairs = pairs.all()
        return pairs

    def log_scout(
        self,
        pair: Pair,
        target_ratio: float,
        current_coin_price: float,
        other_coin_price: float,
    ):
        sh = ScoutHistory(pair=pair, target_ratio=target_ratio, current_coin_price=current_coin_price, other_coin_price=other_coin_price)
        sh.save()
        self.send_update(sh)

    def prune_scout_history(self):
        time_diff = datetime.now() - timedelta(hours=self.config.SCOUT_HISTORY_PRUNE_TIME)
        ScoutHistory.objects(datetime__lt = time_diff).delete()

    def prune_value_history(self):
        session = Session
        # Sets the first entry for each coin for each hour as 'hourly'
        hourly_entries: (
            CoinValue.group_by(CoinValue.coin_id, func.strftime("%H", CoinValue.datetime)).all()
        )
        for entry in hourly_entries:
            entry.interval = Interval.HOURLY

        # Sets the first entry for each coin for each day as 'daily'
        daily_entries: List[CoinValue] = (
            session.query(CoinValue).group_by(CoinValue.coin_id, func.date(CoinValue.datetime)).all()
        )
        for entry in daily_entries:
            entry.interval = Interval.DAILY

        # Sets the first entry for each coin for each month as 'weekly'
        # (Sunday is the start of the week)
        weekly_entries: List[CoinValue] = (
            session.query(CoinValue).group_by(CoinValue.coin_id, func.strftime("%Y-%W", CoinValue.datetime)).all()
        )
        for entry in weekly_entries:
            entry.interval = Interval.WEEKLY

        # The last 24 hours worth of minutely entries will be kept, so
        # count(coins) * 1440 entries
        time_diff = datetime.now() - timedelta(hours=24)
        session.query(CoinValue).filter(
            CoinValue.interval == Interval.MINUTELY, CoinValue.datetime < time_diff
        ).delete()

        # The last 28 days worth of hourly entries will be kept, so count(coins) * 672 entries
        time_diff = datetime.now() - timedelta(days=28)
        session.query(CoinValue).filter(
            CoinValue.interval == Interval.HOURLY, CoinValue.datetime < time_diff
        ).delete()

        # The last years worth of daily entries will be kept, so count(coins) * 365 entries
        time_diff = datetime.now() - timedelta(days=365)
        session.query(CoinValue).filter(
            CoinValue.interval == Interval.DAILY, CoinValue.datetime < time_diff
        ).delete()

        # All weekly entries will be kept forever

    def create_database(self):
        Base.metadata.create_all(self.engine)

    def start_trade_log(self, from_coin: Coin, to_coin: Coin, selling: bool):
        return TradeLog(self, from_coin, to_coin, selling)

    def send_update(self, model):
        if not self.socketio_connect():
            return

        self.socketio_client.emit(
            "update",
            {"table": model.__class__, "data": model.info()},
            namespace="/backend",
        )

    def migrate_old_state(self):
        """
        For migrating from old dotfile format to SQL db. This method should be removed in
        the future.
        """
        if os.path.isfile(".current_coin"):
            with open(".current_coin") as f:
                coin = f.read().strip()
                self.logger.info(f".current_coin file found, loading current coin {coin}")
                self.set_current_coin(coin)
            os.rename(".current_coin", ".current_coin.old")
            self.logger.info(f".current_coin renamed to .current_coin.old - You can now delete this file")

        if os.path.isfile(".current_coin_table"):
            with open(".current_coin_table") as f:
                self.logger.info(f".current_coin_table file found, loading into database")
                table: dict = json.load(f)
                session: Session
                with self.db_session() as session:
                    for from_coin, to_coin_dict in table.items():
                        for to_coin, ratio in to_coin_dict.items():
                            if from_coin == to_coin:
                                continue
                            pair = session.merge(self.get_pair(from_coin, to_coin))
                            pair.ratio = ratio
                            session.add(pair)

            os.rename(".current_coin_table", ".current_coin_table.old")
            self.logger.info(".current_coin_table renamed to .current_coin_table.old - " "You can now delete this file")


class TradeLog:
    def __init__(self, db: Database, from_coin: Coin, to_coin: Coin, selling: bool):
        self.db = db
        session: Session
        with self.db.db_session() as session:
            from_coin = session.merge(from_coin)
            to_coin = session.merge(to_coin)
            self.trade = Trade(from_coin, to_coin, selling)
            session.add(self.trade)
            # Flush so that SQLAlchemy fills in the id column
            session.flush()
            self.db.send_update(self.trade)

    def set_ordered(self, alt_starting_balance, crypto_starting_balance, alt_trade_amount):
        session: Session
        with self.db.db_session() as session:
            trade: Trade = session.merge(self.trade)
            trade.alt_starting_balance = alt_starting_balance
            trade.alt_trade_amount = alt_trade_amount
            trade.crypto_starting_balance = crypto_starting_balance
            trade.state = TradeState.ORDERED
            self.db.send_update(trade)

    def set_complete(self, crypto_trade_amount):
        session: Session
        with self.db.db_session() as session:
            trade: Trade = session.merge(self.trade)
            trade.crypto_trade_amount = crypto_trade_amount
            trade.state = TradeState.COMPLETE
            self.db.send_update(trade)


if __name__ == "__main__":
    database = Database(Logger(), Config())
    # database.create_database()
