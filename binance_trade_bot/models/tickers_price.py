from sqlalchemy import Column, String
from sqlalchemy.sql.sqltypes import DateTime, Float
from datetime import datetime as _datetime

from .base import Base


class TickersPrice(Base):
    __tablename__ = "tickers_price"
    symbol = Column(String, primary_key=True)
    price = Column(Float)
    datetime = Column(DateTime)

    def __init__(self, symbol, price=0.0):
        self.symbol = symbol
        self.price = price
        self.datetime = _datetime.now()

    def __repr__(self):
        return f"<{self.symbol}>"

    def info(self):
        return {"symbol": self.symbol, "price": self.price}
