from mysite import db
from finances.models import transaction
from finances.models.category import categoriesSelectBox

from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from flask_login import current_user, login_required

import json
import datetime
from dateutil.relativedelta import relativedelta

transaction_bp = Blueprint(
    'transaction', 
    __name__, 
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

def _dates():
    today = datetime.date.today()
    if today.day < 12:
        today = today - relativedelta(months=1)

    next_month = today.replace(day=1) + relativedelta(months=1)
    dates = [ next_month - relativedelta(months=12), next_month - datetime.timedelta(days=1) ]

    for i, k in enumerate(['from_date', 'to_date']):
        if request.args.get(k) or k in session:
            s = request.args.get(k) or session[k]
            dates[i] = datetime.date(*[int(x) for x in s.split('-')])

            session[k] = dates[i].strftime('%Y-%m-%d')

    return dates

@transaction_bp.route('/finances/transactions')
@transaction_bp.route('/finances/transactions/<int:category_id>')
@login_required
def transactions(category_id=None):
    return render_template(
        'transactions.html', 
        #table=transaction.transactions(category_id),
        category_id=category_id,
        #categories=categoriesSelectBox(),
    )

@transaction_bp.route('/finances/manual_entry')
@login_required
def manual_entry():
    return render_template(
        'manual_entry.html', 
        date=datetime.date.today().strftime('%Y-%m-%d'),
        categories=categoriesSelectBox()
    )


@transaction_bp.route('/finances/upload_transactions')
@login_required
def upload_transactions():
    return render_template('upload_transactions.html', categories=categoriesSelectBox())

@transaction_bp.route('/finances/monthly_breakdown')
@login_required
def monthly_breakdown():
    from_date, to_date = _dates()
    return render_template(
        'monthly_breakdown.html', 
        table=transaction.monthly_breakdown(from_date, to_date),
    )

@transaction_bp.route('/finances/update_transactions', methods=['POST'])
@login_required
def update_transactions():
    transaction.update_transactions( json.loads(request.form['transactions']) )
    return redirect(url_for('transaction.monthly_breakdown'))



@transaction_bp.route('/rest/finances/transactions/<int:category_id>', methods=['GET', 'POST'])
@login_required
def rest_transactions(category_id):
    return jsonify( transaction.transactions(category_id) )

@transaction_bp.route('/rest/finances/parse_records', methods=['POST'])
@login_required
def rest_parse_records():
    return jsonify({'transactions': transaction.parse_ofx(request.form['text'])})

@transaction_bp.route('/rest/finances/upload_transactions', methods=['POST'])
@login_required
def rest_upload_transactions():
    transaction.save_transactions( current_user.id, json.loads(request.form['transactions']) )
    return jsonify({'results': 'success'})

@transaction_bp.route('/rest/finances/update_transaction/<int:category_id>', methods=['POST'])
@login_required
def rest_update_transaction(category_id):
    transaction.update_transactions([ request.form ])
    return rest_transactions(category_id)

@transaction_bp.route('/rest/finances/manual_entry', methods=['POST'])
@login_required
def rest_manual_entry():
    transaction.add_manual_entry(current_user.id, json.loads(request.form['entry']))
    return jsonify({'results': 'success'})


