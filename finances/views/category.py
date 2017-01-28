from mysite import db
from finances.models.category import Category, categoriesSelectBox
from finances.forms.category import NewCategoryForm

from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from flask_login import current_user, login_required

import json

category_bp = Blueprint(
    'category', 
    __name__, 
    template_folder='../templates',
    static_folder='../static',
    static_url_path='/static/finances',
)


@category_bp.route('/finances/categories', methods=['GET', 'POST'])
@login_required
def categories():
    form = NewCategoryForm(request.form)

    cats = dict([(c.id, c) for c in db.session.query(Category).all()])
    form.parent.choices = categoriesSelectBox()
    if request.method == 'POST' and form.validate_on_submit():
        form.process_input(current_user.id, cats)
        form.parent.choices = categoriesSelectBox()

    return render_template('categories.html', form=form)



@category_bp.route('/rest/finances/categories', methods=['GET'])
@login_required 
def rest_categories():
    top = db.session.query(Category).filter(Category.name=='top').first()
    return jsonify({ 'tree': [top.tree()] })

@category_bp.route('/rest/finances/modify_category', methods=['POST'])
@login_required 
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


