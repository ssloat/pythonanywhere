from mysite import db

from user.models import User, ProviderId
from user.oauth import OAuthSignIn

from flask import Blueprint, render_template, redirect, url_for 
from flask.ext.login import login_user, logout_user, current_user


user_bp = Blueprint('user', __name__, template_folder='templates')

@user_bp.route('/login')
def login():
    return render_template('login.html')

@user_bp.route('/access_denied')
def access_denied():
    return render_template('access_denied.html')

@user_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@user_bp.route('/authorize/<provider>')
def oauth_authorize(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()


@user_bp.route('/callback/<provider>')
def oauth_callback(provider):
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    oauth = OAuthSignIn.get_provider(provider)
    social_id, name, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(name=name, email=email)
        provider_id = ProviderId(id=social_id, user=user)
        db.session.add(user)
        db.session.add(provider_id)
        db.session.commit()

    login_user(user, True)
    return redirect(url_for('index'))


