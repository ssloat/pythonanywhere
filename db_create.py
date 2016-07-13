#!flask/bin/python
from config import SQLALCHEMY_DATABASE_URI
from mysite import db

from flask import Flask

import mysite.user.models
import investments.assets.models
import investments.portfolio.models
import finances.budget.models
import finances.transaction.models

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
 
with app.app_context():
    db.create_all()
