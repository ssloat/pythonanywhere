import os
from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'user.login'

def create_app(obj=None):
    import user.models
    import user.views
    import investments.assets.models
    import investments.assets.views
    import investments.portfolio.models
    import investments.portfolio.views
    import finances.budget.models
    import finances.budget.views
    import finances.transaction.models
    import finances.transaction.views

    app = Flask(__name__)
    app.config.from_object(obj or 'config')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/test')
    def test():
        return render_template('test.html')

    db.init_app(app)
    lm.init_app(app)

    app.register_blueprint(finances.budget.views.budget_bp)
    app.register_blueprint(finances.transaction.views.transaction_bp)
    app.register_blueprint(investments.portfolio.views.portfolio_bp)
    app.register_blueprint(user.views.user_bp)

    Bootstrap(app)

    return app
