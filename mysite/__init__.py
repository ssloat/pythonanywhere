import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'user.login'

import user.models
import user.views
import investments.vanguard.models
import investments.vanguard.views
import investments.stocks.models
import investments.stocks.views
import investments.assets.models
import investments.assets.views
import investments.portfolio.models
import finances.budget.models
import finances.budget.views
import finances.transaction.models
import finances.transaction.views

def create_app(obj=None):
    app = Flask(__name__)
    app.config.from_object(obj or 'config')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')


    db.init_app(app)
    lm.init_app(app)

    app.register_blueprint(finances.budget.views.budget_bp)
    app.register_blueprint(finances.transaction.views.transaction_bp)
    app.register_blueprint(investments.vanguard.views.vanguard_bp)
    #app.register_blueprint(investments.stocks.views.stock_bp)
    app.register_blueprint(user.views.user_bp)

    Bootstrap(app)

    return app
