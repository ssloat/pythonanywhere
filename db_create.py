#!flask/bin/python
from config import SQLALCHEMY_DATABASE_URI
from mysite import db

from flask import Flask

import mysite.user.models
import investments.models.assets
import investments.models.portfolio
import finances.models.budget
import finances.models.transaction
import finances.models.category
import finances.models.pattern

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)
 
with app.app_context():
    db.create_all()
