from mysite import db, lm

from flask.ext.login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)

    provider_ids = db.relationship('ProviderId', backref='user')

class ProviderId(db.Model):
    __tablename__ = 'provider_ids'

    id = db.Column(db.String(128), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, id, user):
        self.id = id
        self.user = user


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

