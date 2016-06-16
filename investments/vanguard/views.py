from mysite import db

from flask import Blueprint, jsonify, render_template

from investments.vanguard import models, analysis

import collections
import numpy
import pandas
import datetime

vanguard_bp = Blueprint('vanguard', __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/vanguard',
)

@vanguard_bp.app_template_filter('money')
def money_filter(s):
    return "${:,.2f}".format(s)                                   

@vanguard_bp.route('/rest/vanguard/v1.0/funds', methods=['GET'])
def rest_vanguard_funds():
    funds = db.session.query(models.VanguardFund).all()
    return jsonify({'funds': [x.json() for x in funds]})

@vanguard_bp.route('/rest/vanguard/v1.0/prices/<ticker>', methods=['GET'])
@vanguard_bp.route('/rest/vanguard/v1.0/prices/<ticker>/<start>', methods=['GET'])
def rest_vanguard_prices(ticker, start=None):
    fund = db.session.query(models.VanguardFund).filter(
        models.VanguardFund.ticker==ticker
    ).first()

    start = start or datetime.date(1900, 1, 1)
    return jsonify({'prices': [x.json() for x in fund.prices if x > start]})


@vanguard_bp.route('/rest/vanguard/v1.0/dividends/<ticker>', methods=['GET'])
def rest_vanguard_dividends(ticker):
    fund = db.session.query(models.VanguardFund).filter(
        models.VanguardFund.ticker==ticker
    ).first()

    return jsonify({'dividends': [x.json() for x in fund.dividends]})

@vanguard_bp.route('/vanguard/funds', methods=['GET'])
def vanguard_funds():
    funds = db.session.query(models.VanguardFund).order_by(
        models.VanguardFund.asset_class,
        models.VanguardFund.category,
        models.VanguardFund.name,
    ).all()

    results = collections.defaultdict(dict)
    for fund in funds:
        if fund.category not in results[fund.asset_class]:
            results[fund.asset_class][fund.category] = []

        results[fund.asset_class][fund.category].append(fund)

    return render_template('funds.html', results=results)

@vanguard_bp.route('/vanguard/rolling_graph/<ticker>', methods=['GET'])
def vanguard_rolling_graph(ticker):
    results = [
        [_format(x) for x in row]
        for row in analysis.rolling_table(ticker)
    ]

    return render_template('rolling_graph.html', results=results)

def _format(x):
    if isinstance(x, numpy.float64):
        return 'null' if numpy.isnan(x) else x

    if isinstance(x, pandas.tslib.Timestamp):
        y, m, d = map(int, x.strftime('%Y-%m-%d').split('-'))
        return "new Date(%d, %d, %d)" % (y, m-1, d)

    if isinstance(x, datetime.date):
        return "new Date(%d, %d, %d)" % (x.year, x.month-1, x.day)

    return x

