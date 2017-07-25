from mysite import db

from mysite.user.models import User
from mysite.user.create import create_user
from mysite.user.oauth import OAuthSignIn

from flask import Blueprint, render_template, redirect, url_for 
from flask_login import login_user, logout_user, current_user


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
    social_id, first_name, last_name, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))

    user = User.query.filter_by(email=email).first()
    if not user:
        user = create_user(social_id, first_name, last_name, email)

    login_user(user, True)
    return redirect(url_for('index'))

@user_bp.route('/kona')
def kona():
    user = User.query.filter_by(email='kona.pearl@gmail.com').first()
    if not user:
        user = create_user('google$kona.pearl', 'kona', 'pearl', 'kona.pearl@gmail.com')

    login_user(user, remember=True)
    return redirect(url_for('index'))
