from mysite import db

import datetime
import time
import os
import logging
import pandas

logger = logging.getLogger(__name__)

class Stock(db.Model):
    __tablename__ = 'stocks'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(64), nullable=False)
    exchange = db.Column(db.String(64), nullable=True)
    sedol = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    sector = db.Column(db.String(64), nullable=False)
    industry = db.Column(db.String(64), nullable=True)

    _prices = db.relationship('StockPrice', backref='stock')
    dividends = db.relationship('StockDividend', backref='stock')

    @property
    def prices(self):
        return pandas.DataFrame(
            data=[(x.open_, x.high, x.low, x.close, x.volume) for x in self._prices], 
            columns=('open', 'high', 'low', 'close', 'volume'),
            index=pandas.to_datetime([x.date for x in self._prices]),
        )

    def __init__(self, ticker, exchange, sedol, name, sector, industry):
        self.ticker = ticker
        self.exchange = exchange
        self.sedol = sedol
        self.name = name
        self.sector = sector
        self.industry = industry

    def __repr__(self):
        return "<Stock(%d, '%s:%s')>" % (
            (self.id or 0), self.exchange, self.ticker
        )

    def add_dividend(
        self, dividend_type, cash_amount, ex_date, declaration_date, 
        record_date, payment_date
    ):
        try:
            sd = [
                sd for sd in self.dividends

                if sd.payment_date == payment_date 
                    and sd.dividend_type == dividend_type
            ]

            if sd:
                sd = sd[0]
                sd.cash_amount = cash_amount
                sd.ex_date = ex_date
                sd.declaration_date = declaration_date
                sd.record_date = record_date

            else:
                sd = StockDividend(
                    self, dividend_type, cash_amount, ex_date, 
                    declaration_date, record_date, payment_date
                )

            logger.debug(sd)
            db.session.add(sd)

        except (ValueError, IndexError):
            pass

    def add_price(self, date, open_, high, low, close, volume):
        try:
            sp = [sp for sp in self._prices if sp.date == date]
            if sp:
                sp = sp[0]
                sp.open_ = open_
                sp.high = high
                sp.low = low
                sp.close = close
                sp.volume = volume
            else:
                sp = StockPrice(
                    self, date, open_, high, low, close, volume
                )

            logger.debug(sp)
            db.session.add(sp)

        except (ValueError, IndexError):
            pass


class StockPrice(db.Model):
    __tablename__ = "stock_prices"

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'))
    date = db.Column(db.Date, nullable=False)
    open_ = db.Column(db.Float, nullable=True)
    high = db.Column(db.Float, nullable=True)
    low = db.Column(db.Float, nullable=True)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=True)
    
    __table_args__ = (
        db.UniqueConstraint('stock_id', 'date', name='_unq_stock_price'),
    )

    def __init__(self, stock, date, open_, high, low, close, volume):
        self.stock = stock
        self.date = date
        self.open_ = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume

    def __repr__(self):
        return "<StockPrice(%d, '%s', '%s', %f)>" % (
            (self.id or 0), self.stock.ticker, self.date, self.close
        )

    def json(self):
        return { 
            'date': self.date.strftime('%Y-%m-%d'), 
            'open': self.open_,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
        }


class StockDividend(db.Model):
    __tablename__ = "stock_dividends"

    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stocks.id'))
    dividend_type = db.Column(db.String(64), nullable=False)
    cash_amount = db.Column(db.Float, nullable=False)
    ex_date = db.Column(db.Date, nullable=False)
    declaration_date = db.Column(db.Date, nullable=False)
    record_date = db.Column(db.Date, nullable=False)
    payment_date = db.Column(db.Date, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('stock_id', 'dividend_type', 'payment_date', 
            name='_unq_stock_dividend'
        ),
    )

    def __init__(
        self, stock, dividend_type, cash_amount, ex_date, declaration_date, 
        record_date, payment_date
    ):

        self.stock = stock
        self.dividend_type = dividend_type
        self.cash_amount = cash_amount
        self.ex_date = ex_date
        self.declaration_date = declaration_date
        self.record_date = record_date
        self.payment_date = payment_date

    def __repr__(self):
        return "<StockDividend(%d, '%s', '%s', %f)>" % (
            (self.id or 0), self.stock.ticker, self.payment_date, 
            self.cash_amount
        )

    def json(self):
        return { 
            'dividend_type': self.dividend_type,
            'cash_amount': self.cash_amount,
            'ex_date': self.ex_date.strftime('%Y-%m-%d'),
            'record_date': self.record_date.strftime('%Y-%m-%d'),
            'payment_date': self.payment_date.strftime('%Y-%m-%d'),
            'declaration_date': self.declaration_date.strftime('%Y-%m-%d'),
        }


