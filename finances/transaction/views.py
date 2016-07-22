from mysite import db
from finances.models.transaction import Transaction, parse_ofx
from finances.models.category import Category, CategoryRE, categoriesSelectBox
from finances.transaction.forms import NewCategoryForm

from flask import Blueprint, jsonify, render_template, request, redirect, url_for
#from flask.ext.login import current_user, login_required

import re

transaction_bp = Blueprint('transaction', __name__, 
    template_folder='../templates',
    static_folder='../static',
    static_url_path='/static/transaction',
)


@transaction_bp.route('/rest/categories', methods=['GET'])
def rest_categories():
    top = db.session.query(Category).filter(Category.name=='top').first()
    return jsonify({ 'tree': [top.tree()] })

@transaction_bp.route('/rest/categories', methods=['POST'])
def rest_modify_category():
    json = request.form

    cat = db.session.query(Category).filter(Category.id==int(json['id'])).first()
    cat.parent_id = int(json['parent_id'])
    cat.depth = 1 + db.session.query(Category).filter(
        Category.id==cat.parent_id
    ).first().depth

    db.session.add(cat)
    db.session.commit()

    return jsonify({})

@transaction_bp.route('/rest/upload', methods=['POST'])
def rest_upload():
    return jsonify({'transactions': parse_ofx(request.form['text'])})

@transaction_bp.route('/rest/upload_transactions', methods=['POST'])
def rest_upload_transactions():
    transactions = request.form['transactions'];

    return jsonify({'results': 'success'})


@transaction_bp.route('/categories', methods=['GET', 'POST'])
def categories():
    form = NewCategoryForm(request.form)

    cats = dict([(c.id, c) for c in db.session.query(Category).all()])
    form.parent.choices = [(c.id, c.name) for c in cats.values()]

    if request.method == 'POST' and form.validate_on_submit():
        form.process_input(cats)

    return render_template('categories.html', form=form)

@transaction_bp.route('/upload')
def upload():
    return render_template('upload.html', categories=categoriesSelectBox())
