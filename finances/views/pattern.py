from mysite import db
from finances.models import pattern as pattern_model
from finances.models.category import categoriesSelectBox

from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from flask_login import current_user, login_required

import json
import datetime
from dateutil.relativedelta import relativedelta

pattern_bp = Blueprint(
    'pattern', 
    __name__, 
    template_folder='../templates',
    static_folder='../static',
    static_url_path='/static/finances',
)

@pattern_bp.app_template_filter('money')
def money_filter(s):
    return "${:,.2f}".format(s)

@pattern_bp.app_template_filter('comma')
def comma_filter(s):
    return "{:,.2f}".format(s)



@pattern_bp.route('/finances/pattern/<int:pattern_id>')
@login_required
def pattern(pattern_id):
    return render_template(
        'pattern.html', 
        **(pattern_model.pattern(current_user.id, pattern_id))
    )

@pattern_bp.route('/finances/patterns')
@login_required
def patterns():
    return render_template('patterns.html')

@pattern_bp.route('/rest/finances/patterns', methods=['GET'])
@login_required
def rest_patterns():
    return jsonify(
        {'rows': pattern_model.patterns(current_user.id)}
    )

@pattern_bp.route('/rest/finances/pattern_search', methods=['POST'])
@login_required
def rest_pattern_search():
    return jsonify(
        {'rows': pattern_model.search(current_user.id, request.form['text'])}
    )
