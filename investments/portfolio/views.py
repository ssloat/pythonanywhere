import collections
import datetime
import time
import json
import math
import itertools
from dateutil.relativedelta import relativedelta

from investments.portfolio.models import Portfolio, Position
from investments.assets.models import Asset
from mysite import db

from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from flask.ext.login import current_user, login_required

portfolio_bp = Blueprint('portfolio', __name__, 
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/portfolio',
)

@portfolio_bp.app_template_filter('money')
def money_filter(s):
    return "{:,.2f}".format(s) if isinstance(s, (int, float)) else s

 
@portfolio_bp.route('/portfolio/<int:portfolio_id>/<start>')
def portfolio(portfolio_id, start):
    start = datetime.date(*map(int, start.split('-')))
    p = db.session.query(Portfolio).filter(Portfolio.id==portfolio_id).first()
    #if p.user_id != current_user.id:
    #    return redirect(url_for('user.access_denied'))

    values, returns = p.table_categories(start, datetime.date(2016, 12, 31))

    return render_template('portfolio.html', values=values, returns=returns)
 
@portfolio_bp.route('/positions/<int:portfolio_id>/<start>')
def positions(portfolio_id, start):
    start = datetime.date(*map(int, start.split('-')))
    portfolio = db.session.query(Portfolio).filter(Portfolio.id==portfolio_id).first()
    #if p.user_id != current_user.id:
    #    return redirect(url_for('user.access_denied'))

    positions = [p for p in portfolio.positions if p.date >= start and p.action == 'Buy']

    sp500 = db.session.query(Asset).filter(Asset.ticker=='VFINX').first()
    results = []
    for position in positions:
        comp = Position(
            portfolio, position.date, sp500, position.cost/sp500.price(position.date), 
            position.cost, sp500.price(position.date), 'Buy'
        )

        dates = sorted([p.date for p in position.asset.prices if p.date >= position.date])
        table = {
            'cols': [
                {'label': 'Date', 'type': 'date'},
                {'label': position.asset.ticker, 'type': 'number'},
                {'label': 'SP500', 'type': 'number'},
            ],
            'rows': [
                {'c': [
                    {'v': 'Date(%d,%d,%d)' % (d.year, d.month-1, d.day)},
                    {'v': position.change(d)},
                    {'v': comp.change(d)},
                ]}
                for d in dates
            ]
        }

        results.append((position, json.dumps(table)))

    return render_template('positions.html', results=results)

@portfolio_bp.route('/interval_investing/<ticker>/<amount>/<start>')
def interval_investing(ticker, amount, start):
    amount = float(amount)
    start = datetime.date(*map(int, start.split('-')))

    asset = db.session.query(Asset).filter(Asset.ticker==ticker).first()
    shares = 0

    table = {
        'cols': [
            {'label': 'Date', 'type': 'date'},
            {'label': 'value', 'type': 'number'},
            {'label': 'apy', 'type': 'number'},
            {'label': 'cost', 'type': 'number'},
        ],
        'rows': [],
    }

    results = []
    last = max([p.date for p in asset.prices])
    date = start
    for intervals in itertools.count(1):
        price = asset.price_ff(date)
        shares += amount / price
        cost = intervals*amount
        value = shares*price
        ret = (value-cost)/cost
        apy = math.pow(1+ret, 1.0/(intervals/12.0)) - 1
        results.append((date, cost, value, 100*ret, 100*apy))

        table['rows'].append({'c': [
            {'v': 'Date(%d,%d,%d)' % (date.year, date.month-1, date.day)},
            {'v': value},
            {'v': apy},
            {'v': cost},
        ]})

        next_date = start + relativedelta(months=intervals)
        if next_date > last:
            break

        dividends = [d for d in asset.dividends if d.date >= date and d.date < next_date]
        for div in dividends:
            shares += shares*div.value / asset.price_ff(div.date)

        date = next_date

    return render_template('interval_investing.html', results=results, table=table)


    
