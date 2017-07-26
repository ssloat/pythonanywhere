import logging

from flask_testing import TestCase

from mysite import create_app, db
from mysite.models.user import User

class TestBase(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True

    def create_app(self):
        return create_app(self)

    def setUp(self):
        logging.basicConfig(level=logging.ERROR)
        db.create_all()

        self.user = User(id=1, email='user@host.com', name='test', first_name='test', last_name='test') 
        db.session.add(self.user)

    def tearDown(self):
        db.session.remove()
        db.drop_all()

