import os
from flask import Flask
from flask_bootstrap import Bootstrap
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)
Bootstrap(app)
app.config.from_object('config')

db = SQLAlchemy(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

import mysite.views
import mysite.vanguard.models
import mysite.vanguard.views
import mysite.user.models
import mysite.user.views
import mysite.stocks.models
import mysite.stocks.views
import mysite.budget.models
import mysite.budget.views
