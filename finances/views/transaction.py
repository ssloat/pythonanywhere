from mysite import db
from finances.models import transaction
from finances.models.category import categoriesSelectBox

from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from flask.ext.login import current_user, login_required

import json

transaction_bp = Blueprint('transaction', __name__, 
    template_folder='../templates',
    static_folder='../static',
    static_url_path='/static/finances',
)

@transaction_bp.app_template_filter('money')
def money_filter(s):
    return "${:,.2f}".format(s)

@transaction_bp.app_template_filter('comma')
def comma_filter(s):
    return "{:,.2f}".format(s)


@login_required
@transaction_bp.route('/finances/transactions')
@transaction_bp.route('/finances/transactions/<category_id>')
def transactions(category_id=None):
    return render_template(
        'transactions.html', 
        table=transaction.transactions(category_id),
        categories=categoriesSelectBox(),
    )

@login_required
@transaction_bp.route('/finances/upload_transactions')
def upload_transactions():
    return render_template('upload_transactions.html', categories=categoriesSelectBox())

@login_required
@transaction_bp.route('/finances/monthly_breakdown')
def monthly_breakdown():
    import datetime
    start = datetime.date(2016, 1, 1)
    end = datetime.date(2016, 6, 30)
    return render_template(
        'monthly_breakdown.html', 
        table=transaction.monthly_breakdown(start, end), 
    )

@login_required
@transaction_bp.route('/finances/update_transactions', methods=['POST'])
def update_transactions():
    transaction.update_transactions( json.loads(request.form['transactions']) )
    return redirect(url_for('transaction.monthly_breakdown'))



@login_required
@transaction_bp.route('/rest/finances/parse_records', methods=['POST'])
def rest_parse_records():
    return jsonify({'transactions': transaction.parse_ofx(request.form['text'])})

@login_required
@transaction_bp.route('/rest/finances/upload_transactions', methods=['POST'])
def rest_upload_transactions():
    transaction.save_transactions( json.loads(request.form['transactions']) )
    return jsonify({'results': 'success'})

@login_required
@transaction_bp.route('/rest/finances/update_transactions', methods=['POST'])
def rest_update_transactions():
    transaction.update_transactions( json.loads(request.form['transactions']) )
    return jsonify({'results': 'success'})


