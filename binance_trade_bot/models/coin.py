from mongoengine import Document, fields

from .base import Base


class Coin(Document):
    # __tablename__ = "coins"
    symbol = fields.StringField()
    enabled = fields.BooleanField(default=True)

    # def __init__(self, symbol, enabled=True):
    #     self.symbol = symbol
    #     self.enabled = enabled
    def __str__(self):
        return self.symbol

    def __add__(self, other):
        if isinstance(other, str):
            return self.symbol + other
        if isinstance(other, Coin):
            return self.symbol + other.symbol
        raise TypeError(f"unsupported operand type(s) for +: 'Coin' and '{type(other)}'")

    def __repr__(self):
        return f"<{self.symbol}>"

    def info(self):
        return {"symbol": self.symbol, "enabled": self.enabled}
