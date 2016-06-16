import datetime 

from mysite import db

from investments.assets.models import Asset, AssetPrice

from base_test import TestBase

class MyTest(TestBase):
    def setUp(self):
        super(MyTest, self).setUp()

        asset = Asset(ticker='TEST', fund_type='Stock', asset_class='Class', category='Category')
        db.session.add(asset)
        db.session.commit()

    def test_asset(self):
        asset = db.session.query(Asset).first()
        self.assertTrue(asset.ticker == 'TEST')


