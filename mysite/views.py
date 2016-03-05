from . import app, db
from mysite.models.user import User
from mysite.models.vanguard import VanguardFund, VanguardPrice, VanguardDividend

from flask import render_template, redirect, url_for, jsonify
from flask.ext.login import login_user, logout_user, current_user

from oauth import OAuthSignIn


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@app.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, nickname=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)
    return redirect(url_for('index'))


@app.route('/rest/vanguard/v1.0/funds', methods=['GET'])
def vanguard_funds():
    resp = [
        {
            'id': x.id,
            'name': x.name,
            'fund_type': x.fund_type,
            'ticker': x.ticker,
            'asset_class': x.asset_class,
            'exp_ratio': x.exp_ratio,
            'category': x.category,
            'minimum': x.minimum,
        }
        for x in db.session.query(VanguardFund).all()
    ]

    return jsonify({'funds': resp})

@app.route('/rest/vanguard/v1.0/prices/<ticker>', methods=['GET'])
def vanguard_prices(ticker):
    resp = [
        { 'date': x.date.strftime('%Y-%m-%d'), 'price': x.price }
        for x in db.session.query(VanguardFund).filter(
            VanguardFund.ticker==ticker
        ).first().prices
    ]

    return jsonify({'prices': resp})

@app.route('/rest/vanguard/v1.0/dividends/<ticker>', methods=['GET'])
def vanguard_dividends(ticker):
    resp = [
        { 
            'dividend_type': x.dividend_type,
            'price_per_share': x.price_per_share,
            'payable_date': x.payable_date.strftime('%Y-%m-%d'),
            'record_date': x.record_date.strftime('%Y-%m-%d'),
            'reinvest_date': x.reinvest_date.strftime('%Y-%m-%d'),
            'reinvest_price': x.reinvest_price,
        }
        for x in db.session.query(VanguardFund).filter(
            VanguardFund.ticker==ticker
        ).first().dividends
    ]

    return jsonify({'dividends': resp})
