from mongoengine import fields, Document, EmbeddedDocumentField
from .base import Base
from .coin import Coin


class Pair(Document):

    from_coin = fields.ReferenceField(Coin)
    to_coin = fields.ReferenceField(Coin)
    ratio = fields.FloatField()

    # enabled = column_property(
    #     select([func.count(Coin.symbol) == 2])
    #     .where(or_(Coin.symbol == from_coin_id, Coin.symbol == to_coin_id))
    #     .where(Coin.enabled.is_(True))
    # )

    # def __init__(self, from_coin: Coin, to_coin: Coin, ratio=None):
    #     self.from_coin = from_coin
    #     self.to_coin = to_coin
    #     self.ratio = ratio

    def __repr__(self):
        return f"<{self.from_coin_id}->{self.to_coin_id} :: {self.ratio}>"

    def info(self):
        return {
            "from_coin": self.from_coin.info(),
            "to_coin": self.to_coin.info(),
            "ratio": self.ratio,
        }
