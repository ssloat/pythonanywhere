import os
from flask import Flask, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
lm = LoginManager()
lm.login_view = 'user.login'

def create_app(obj=None):
    import mysite.user.views
    import investments.views.assets
    import investments.views.portfolio
    import finances.views.budget
    import finances.views.transaction
    import finances.views.pattern
    import finances.views.category

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

    app.register_blueprint(finances.views.budget.budget_bp)
    app.register_blueprint(finances.views.transaction.transaction_bp)
    app.register_blueprint(finances.views.pattern.pattern_bp)
    app.register_blueprint(finances.views.category.category_bp)
    app.register_blueprint(investments.views.portfolio.portfolio_bp)
    app.register_blueprint(mysite.user.views.user_bp)

    Bootstrap(app)

    return app
