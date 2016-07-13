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
        asset2 = Asset(ticker='TEST2', fund_type='Stock', asset_class='Class', category='Category')
        portfolio = Portfolio(user, 'Test Portfolio')
        position = Position(portfolio, datetime.date(2016, 5, 2), asset, 1, 97.25, 97.25, 'BUY')
        position2 = Position(portfolio, datetime.date(2016, 5, 2), asset2, 1, 87.25, 87.25, 'BUY')

        db.session.add(user)
        db.session.add(portfolio)
        db.session.add(asset)
        db.session.add(asset2)
        db.session.add(position)
        db.session.add(position2)

        db.session.add(AssetPrice(id=1, ticker=asset.ticker, date=datetime.date(2016, 5, 2), close=97.25))
        db.session.add(AssetPrice(id=2, ticker=asset.ticker, date=datetime.date(2016, 5, 3), close=97.5))
        db.session.add(AssetPrice(id=3, ticker=asset.ticker, date=datetime.date(2016, 5, 4), close=96.75))
        db.session.add(AssetPrice(id=4, ticker=asset.ticker, date=datetime.date(2016, 5, 5), close=97.75))

        db.session.add(AssetPrice(id=5, ticker=asset2.ticker, date=datetime.date(2016, 5, 2), close=87.25))
        db.session.add(AssetPrice(id=6, ticker=asset2.ticker, date=datetime.date(2016, 5, 3), close=87.5))
        db.session.add(AssetPrice(id=7, ticker=asset2.ticker, date=datetime.date(2016, 5, 4), close=86.75))
        db.session.add(AssetPrice(id=8, ticker=asset2.ticker, date=datetime.date(2016, 5, 5), close=87.75))

        db.session.commit()

    def test_position(self):
        portfolio = db.session.query(Portfolio).first()
        self.assertTrue(portfolio.name == 'Test Portfolio')
        self.assertTrue(len(portfolio.positions) == 2)

    def test_dates(self):
        portfolio = db.session.query(Portfolio).first()
        self.assertEquals(
            portfolio.dates(datetime.date(2016, 5, 3), datetime.date(2016, 5, 4)),
            [datetime.date(2016, 5, 3), datetime.date(2016, 5, 4)]
        )

    def test_costs(self):
        portfolio = db.session.query(Portfolio).first()

        costs = portfolio.costs(datetime.date(2016, 5, 9))
        print costs
        self.assertEquals(costs, {'TEST': 97.25, 'TEST2': 87.25})

