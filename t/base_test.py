import logging

from flask.ext.testing import TestCase

from mysite import create_app, db


class TestBase(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = True

    def create_app(self):
        return create_app(self)

    def setUp(self):
        logging.basicConfig(level=logging.ERROR)
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

