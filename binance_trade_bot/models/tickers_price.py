from datetime import datetime as _datetime
from mongoengine import Document, fields
from .base import Base


class TickersPrice(Document):
    symbol = fields.StringField()
    price = fields.FloatField()
    datetime = fields.DateTimeField()

    def __init__(self, symbol, price=0.0):
        self.symbol = symbol
        self.price = price
        self.datetime = _datetime.now()

    def __repr__(self):
        return f"<{self.symbol}>"

    def info(self):
        return {"symbol": self.symbol, "price": self.price}
