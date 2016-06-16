import datetime 

from mysite import db

from user.models import User
from investments.assets.models import Asset, AssetPrice
from investments.portfolio.models import Portfolio, Position

from base_test import TestBase

class MyTest(TestBase):
    def setUp(self):
        super(MyTest, self).setUp()

        user = User(id=1, email='user@host.com', name='Test User')
        asset = Asset(ticker='TEST', fund_type='Stock', asset_class='Class', category='Category')
        portfolio = Portfolio(user, 'Test Portfolio')
        position = Position(portfolio, datetime.date(2016, 5, 2), asset, 1, 97.25, 97.25, 'BUY')

        db.session.add(user)
        db.session.add(portfolio)
        db.session.add(asset)
        db.session.add(position)

        db.session.add(AssetPrice(id=1, ticker=asset.ticker, date=datetime.date(2016, 5, 2), close=97.25))
        db.session.add(AssetPrice(id=2, ticker=asset.ticker, date=datetime.date(2016, 5, 3), close=97.5))
        db.session.add(AssetPrice(id=3, ticker=asset.ticker, date=datetime.date(2016, 5, 4), close=96.75))
        db.session.add(AssetPrice(id=4, ticker=asset.ticker, date=datetime.date(2016, 5, 5), close=97.75))

        db.session.commit()

    def test_position(self):
        portfolio = db.session.query(Portfolio).first()
        self.assertTrue(portfolio.name == 'Test Portfolio')
        self.assertTrue(len(portfolio.positions) == 1)


