from datetime import datetime

from mongoengine import Document, fields
from .base import Base
from .coin import Coin


class CurrentCoin(Document):  # pylint: disable=too-few-public-methods
    # __tablename__ = "current_coin_history"
    coin = fields.ReferenceField(Coin)
    datetime = fields.DateTimeField(default=datetime.utcnow)

    def info(self):
        return {"datetime": self.datetime.isoformat(), "coin": self.coin.info()}
