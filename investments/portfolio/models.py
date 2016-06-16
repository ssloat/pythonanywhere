from mysite import db

from investments.assets.models import Asset, AssetPrice
import datetime

class Portfolio(db.Model):
    __tablename__ = 'portfolios'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(64), nullable=False)
    positions = db.relationship('Position', backref='portfolio')

    user = db.relationship('User')

    def __init__(self, user, name):
        self.user = user
        self.name = name

        self.entries = {}

    def value(self, date):
        return sum(self.values(date).values(), 0.0)

    def values(self, date):
        positions = [p for p in self.positions if p.date <= date]
        
        results = {}
        start = date + datetime.timedelta(days=-5)
        for asset in set([p.asset for p in positions]):
            shares = sum([p.shares for p in positions if p.asset == asset], 0.0)

            p = asset.price(date)
            if p:
                results[asset.ticker] = shares * p

        return results


class Position(db.Model):
    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolios.id'))

    date = db.Column(db.Date)
    asset_id = db.Column(db.String(64), db.ForeignKey('assets.ticker'))
    shares = db.Column(db.Float)
    action = db.Column(db.String(64))
    cost = db.Column(db.Float)
    price = db.Column(db.Float)

    asset = db.relationship('Asset')

    def __init__(self, portfolio, date, asset, shares, cost, price, action):
        self.portfolio = portfolio
        self.date = date

        if isinstance(asset, str):
            self.asset_id = asset
        else:
            self.asset = asset

        self.action = action
        self.cost = cost
        self.shares = shares
        self.price = price

    def __repr__(self):
        return "<Position(%s, %s, '%s' %f, %f, %f)>" % (
            self.date, self.asset, self.action, self.cost, self.shares, self.price
        )

def portfolio(start, end):
    dates = []
    while end > start:
        dates.append(end)

        end = end.replace(day=1)
        end = end - datetime.timedelta(days=1)

    p = Portfolio()
    p.add_401k()
    
    results = {'headings': [''] + [str(d) for d in dates], 'rows': [{'name': 'top'}]}

    for acc in ['BROKERAGE', '401k', 'ROTH']:
        acc_results = [] #{'name': acc, 'parent': 'top', 'values': [0.0 for d in dates]})

        for fund in sorted(p.entries[acc].keys()):
            data = [x[-1] for x in p.historical_values(acc, fund, dates)]
            if [x for x in data if x != 0.0]:
                acc_results.append({'name': fund, 'data': data, 'parent': acc.capitalize()})

        data = [sum(x) for x in zip(*[y['data'] for y in acc_results])]
        heading = {'name': acc.capitalize(), 'parent': 'top', 'data': data}
        results['rows'].extend([heading] + acc_results)

    return results

def fundprices(fund, start, end):
    prices = db.session.query(AssetPrice).join(Asset).filter(
        Asset.name==fund, AssetPrice.date>=start, AssetPrice.date<=end
    ).order_by(db.desc(AssetPrice.date))

    return [{'date': p.date, 'price': p.close} for p in prices]

  