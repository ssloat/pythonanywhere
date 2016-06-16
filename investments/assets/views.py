from mysite import db

from flask import Blueprint, jsonify

from investments.assets import models

asset_bp = Blueprint('asset', __name__)

@asset_bp.route('/rest/asset/v1.0/list', methods=['GET'])
def rest_assets():
    funds = db.session.query(models.Asset).all()
    return jsonify({'assets': [x.json() for x in funds]})

@asset_bp.route('/rest/asset/v1.0/prices/<ticker>', methods=['GET'])
def rest_asset_prices(ticker):
    asset = db.session.query(models.Asset).filter(
        models.Asset.ticker==ticker
    ).first()

    return jsonify({'prices': [x.json() for x in asset.prices]})


