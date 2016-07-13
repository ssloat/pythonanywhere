import collections

from mysite import db
from finances.budget.models import Budget, Item
from finances.budget.forms import NewBudgetForm

from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from flask.ext.login import current_user, login_required

budget_bp = Blueprint('budget', __name__, 
    template_folder='templates',
    static_folder='static',
    static_url_path='/static/budget',
)

@budget_bp.app_template_filter('money')
def money_filter(s):
    return "{:,.2f}".format(s)

@budget_bp.route('/rest/budget/<int:budget_id>', methods=['GET'])
@login_required
def rest_budget(budget_id):
    b = db.session.query(Budget).filter(Budget.id==budget_id).first()
    if b.user_id != current_user.id:
        return jsonify({'error': 'access denied'})

    data = {'name': b.name, 'rows': b.html() }
    return jsonify(data)

@budget_bp.route('/rest/add_item/<int:budget_id>', methods=['POST'])
@login_required
def rest_add_item(budget_id):
    b = db.session.query(Budget).filter(Budget.id==budget_id).first()
    if b.user_id != current_user.id:
        return jsonify({'error': 'access denied'})

    json = request.form

    monthly = float(json['monthly']) / 12.0 if json['monthly'] else 0.0
    yearly = float(json['yearly']) if json['yearly'] else 0.0

    db.session.add( 
        Item(b, json['category'], json['name'], monthly, yearly) 
    )
    db.session.commit()

    return rest_budget(budget_id)
    
@budget_bp.route('/rest/remove_item/<int:budget_id>', methods=['POST'])
@login_required
def rest_remove_item(budget_id):
    b = db.session.query(Budget).filter(Budget.id==budget_id).first()
    if b.user_id != current_user.id:
        return jsonify({'error': 'access denied'})

    json = request.form

    db.session.query(Item).filter(Item.id==json['dbid']).delete()
    db.session.commit()

    return rest_budget(budget_id)
 
@budget_bp.route('/budget/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def budget(budget_id):
    b = db.session.query(Budget).filter(Budget.id==budget_id).first()
    if b.user_id != current_user.id:
        return redirect(url_for('user.access_denied'))

    return render_template('budget.html', budget_id=budget_id)

@budget_bp.route('/budgets', methods=['GET', 'POST'])
@login_required
def budgets():
    form = NewBudgetForm(request.form)

    if request.method == 'POST' and form.validate_on_submit():
        json = request.form
        b = Budget(current_user.id, json['name'], int(json['year']), json['status'])
        db.session.add(b)
        db.session.commit()
        return redirect(url_for('budget.budget', budget_id=b.id))

    budgets = db.session.query(Budget).filter(Budget.user_id==current_user.id).all()
    return render_template('budgets.html', form=form, budgets=budgets)

