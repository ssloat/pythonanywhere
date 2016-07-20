from mysite import db

import datetime
import time
import os
import logging
import itertools

logger = logging.getLogger(__name__)

"""
DEFINER VIEW `assets` AS 
select 
   `vanguard_funds`.`fund_type` AS `fund_type`,`vanguard_funds`.`asset_class` AS `asset_class`,
   `vanguard_funds`.`category` AS `category`,`vanguard_funds`.`ticker` AS `ticker` 
from `vanguard_funds` 
union select 
   'Stock' AS `fund_type`,`stocks`.`sector` AS `asset_class`,`stocks`.`industry` AS `category`,
   `stocks`.`ticker` AS `ticker` 
from `stocks` 


insert into assets select ticker, fund_type, asset_class, category from vanguard_funds;
insert into assets select ticker, 'Stock', sector, industry from stocks;
"""

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

"""
create view asset_prices as
select concat('STOCK-', sp.id) as id, s.ticker as ticker, sp.date as date, sp.close as close,
   sp.open_ as open_, sp.high as high, sp.low as low, sp.volume as volume
from stocks s, stock_prices sp where sp.stock_id = s.id
union
select concat('VANGUARD-', vp.id) as id, vf.ticker as ticker, vp.date as date, vp.price as close,
   null as open_, null as high, null as low, null as volume
from vanguard_funds vf, vanguard_prices vp where vp.fund_id=vf.id

insert into asset_prices (ticker, date, close) select ticker, date, price from vanguard_prices vp, vanguard_funds vf where vp.fund_id=vf.id;
insert into asset_prices (ticker, date, close, open_, high, low, volume) select s.ticker, date, close, open_, high, low, volume from stocks s, stock_prices sp where sp.stock_id=s.id;
"""

class AssetPrice(db.Model):
    __tablename__ = "asset_prices"

    #id = db.Column(db.String(64), primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(64), db.ForeignKey('assets.ticker'))
    date = db.Column(db.Date, nullable=False)
    close = db.Column(db.Float, nullable=False)
    open_ = db.Column(db.Float, nullable=True)
    high = db.Column(db.Float, nullable=True)
    low = db.Column(db.Float, nullable=True)
    volume = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return "<AssetPrice(%d, '%s', '%s', %f)>" % (
            (self.id or 0), self.ticker, self.date, self.close
        )

    def json(self):
        return { 
            'date': self.date.strftime('%Y-%m-%d'), 
            'close': self.close,
        }

"""
insert into asset_dividends (ticker, date, value) select vf.ticker, reinvest_date, price_per_share from vanguard_funds vf, vanguard_dividends vd where vd.fund_id=vf.id;
"""

class AssetDividend(db.Model):
    __tablename__ = "asset_dividends"

    #id = db.Column(db.String(64), primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
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


