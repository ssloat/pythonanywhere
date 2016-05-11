import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'user.login'

#import mysite.vanguard.models
#import mysite.vanguard.views
#import mysite.stocks.models
#import mysite.stocks.views
import user.models
import user.views
import budget.models
import budget.views

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')


    db.init_app(app)
    lm.init_app(app)

    app.register_blueprint(budget.views.budget_bp)
    app.register_blueprint(user.views.user_bp)

    Bootstrap(app)

    return app
