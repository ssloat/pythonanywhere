from mysite import db

import datetime
import time
import os
import logging
import itertools

logger = logging.getLogger(__name__)

class Asset(db.Model):
    __tablename__ = 'assets'

    ticker = db.Column(db.String(64), primary_key=True)
    fund_type = db.Column(db.String(64), nullable=False)
    asset_class = db.Column(db.String(64), nullable=False)
    category = db.Column(db.String(64), nullable=False)

    prices = db.relationship('AssetPrice', backref='asset')
    dividends = db.relationship('AssetDividend', backref='asset')

    def price(self, date):
        prices = filter(lambda p: p.date == date, self.prices)
        return prices[0].close if prices else None

    def price_ff(self, date):
        prices = filter(
            lambda p: p.date <= date, 
            sorted(self.prices, cmp=lambda x, y: cmp(x.date, y.date))
        )
        return prices[-1].close if prices else self.prices[-1]

class AssetPrice(db.Model):
    __tablename__ = "asset_prices"

    id = db.Column(db.String(64), primary_key=True)
    ticker = db.Column(db.String(64), db.ForeignKey('assets.ticker'))
    date = db.Column(db.Date, nullable=False)
    close = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return "<AssetPrice(%d, '%s', '%s', %f)>" % (
            (self.id or 0), self.ticker, self.date, self.close
        )

    def json(self):
        return { 
            'date': self.date.strftime('%Y-%m-%d'), 
            'close': self.close,
        }


class AssetDividend(db.Model):
    __tablename__ = "asset_dividends"

    id = db.Column(db.String(64), primary_key=True)
    ticker = db.Column(db.String(64), db.ForeignKey('assets.ticker'))
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return "<AssetDividend(%d, '%s', '%s', %f)>" % (
            (self.id or 0), self.ticker, self.date, self.value
        )

    def json(self):
        return { 
            'date': self.date.strftime('%Y-%m-%d'), 
            'value': self.value,
        }


