import enum
from datetime import datetime as _datetime


from mongoengine import fields
from mongoengine.document import Document
from .base import Base
from .coin import Coin


class Interval(enum.Enum):
    MINUTELY = "MINUTELY"
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"


class CoinValue(Document):
    coin = fields.ReferenceField(Coin)
    balance = fields.FloatField()
    usd_price = fields.FloatField()
    btc_price = fields.FloatField()
    interval = fields.IntField(default=Interval.MINUTELY)
    datetime = fields.DateTimeField(default=_datetime.now)

    # def __init__(
    #     self,
    #     coin: str,
    #     balance: float,
    #     usd_price: float,
    #     btc_price: float,
    #     interval=Interval.MINUTELY,
    #     datetime: _datetime = None,
    # ):
    #     self.coin = coin
    #     self.balance = balance
    #     self.usd_price = usd_price
    #     self.btc_price = btc_price
    #     self.interval = interval
    #     self.datetime = datetime or _datetime.now()


    def usd_value(self):
        if self.usd_price is None:
            return None
        return self.balance * self.usd_price

    # @usd_value.expression
    # def usd_value(self):
    #     return self.balance * self.usd_price

    def btc_value(self):
        if self.btc_price is None:
            return None
        return self.balance * self.btc_price

    # @btc_value.expression
    # def btc_value(self):
    #     return self.balance * self.btc_price

    def info(self):
        return {
            "balance": self.balance,
            "usd_value": self.usd_value,
            "btc_value": self.btc_value,
            "datetime": self.datetime.isoformat(),
        }
