import enum
from datetime import datetime

from mongoengine import Document, fields
from .base import Base
from .coin import Coin


class TradeState(enum.Enum):
    STARTING = "STARTING"
    ORDERED = "ORDERED"
    COMPLETE = "COMPLETE"


class Trade(Document):
    alt_coin = fields.ReferenceField(Coin)

    crypto_coin_id = fields.ReferenceField(Coin)

    selling = fields.BooleanField()

    state = fields.StringField(choices=TradeState, default=TradeState.STARTING)

    alt_starting_balance = fields.FloatField()
    alt_trade_amount = fields.FloatField()
    crypto_starting_balance = fields.FloatField()
    crypto_trade_amount = fields.FloatField()

    datetime = fields.DateTimeField(default=datetime.utcnow)

    # def __init__(self, alt_coin: str, crypto_coin: str, selling: bool):
    #     self.alt_coin = alt_coin
    #     self.crypto_coin = crypto_coin
    #     self.state = TradeState.STARTING
    #     self.selling = selling
    #     self.datetime = datetime.utcnow()

    def info(self):
        return {
            "id": self.id,
            "alt_coin": self.alt_coin.info(),
            "crypto_coin": self.crypto_coin.info(),
            "selling": self.selling,
            "state": self.state.value,
            "alt_starting_balance": self.alt_starting_balance,
            "alt_trade_amount": self.alt_trade_amount,
            "crypto_starting_balance": self.crypto_starting_balance,
            "crypto_trade_amount": self.crypto_trade_amount,
            "datetime": self.datetime.isoformat(),
        }
