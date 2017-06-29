from mysite import db, lm

from flask_login import UserMixin
from sqlalchemy.ext.declarative import declared_attr

from finances.models.category import Category

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    name = db.Column(db.String(64), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=True)

    provider_ids = db.relationship('ProviderId', backref='user')

class ProviderId(db.Model):
    __tablename__ = 'provider_ids'

    id = db.Column(db.String(128), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, id, user):
        self.id = id
        self.user = user

def create_user(social_id, first_name, last_name, email):
    user = User(
        first_name=first_name,
        last_name=last_name,
        name=' '.join([first_name, last_name]),
        email=email
    )
    provider_id = ProviderId(id=social_id, user=user)
    db.session.add(user)
    db.session.add(provider_id)

    top = Category(user, 'top')
    uncat = Category(user, 'uncategorized', top)
    db.session.add(top)
    db.session.add(uncat)

    db.session.commit()
    return user
        

class AddUser(object):
    
    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey('users.id'))

    @declared_attr
    def user(cls):
        return db.relationship('User')

    def __init__(self, user):
        if isinstance(user, (int, long)):
            self.user_id = user
        else:
            self.user = user


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

