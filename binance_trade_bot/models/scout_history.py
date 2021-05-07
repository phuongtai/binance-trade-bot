from datetime import datetime

from mongoengine import Document, fields
from .base import Base
from .pair import Pair


class ScoutHistory(Document):


    pair = fields.ReferenceField(Pair)
    target_ratio = fields.FloatField()
    current_coin_price = fields.FloatField()
    other_coin_price = fields.FloatField()

    datetime = fields.DateTimeField(default=datetime.utcnow)


    def current_ratio(self):
        return self.current_coin_price / self.other_coin_price

    def info(self):
        return {
            "from_coin": self.pair.from_coin.info(),
            "to_coin": self.pair.to_coin.info(),
            "current_ratio": self.current_ratio,
            "target_ratio": self.target_ratio,
            "current_coin_price": self.current_coin_price,
            "other_coin_price": self.other_coin_price,
            "datetime": self.datetime.isoformat(),
        }
