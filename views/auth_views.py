"""
Auth views
"""

from flask import Blueprint, render_template, session, redirect, url_for
from constants import LOGIN_PAGE_ROUTE, LOGIN_ROUTE, LOGIN_TEMPLATE, AUTH_BLUEPRINT_NAME
from authlib.integrations.flask_client import OAuth
import os

oauth = OAuth()
google = None

def init_oauth(app):
    """Initialize OAuth and register Google provider."""
    global google
    oauth.init_app(app)

    google = oauth.register(
        name='google',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        client_kwargs={'scope': 'openid email profile'}
    )

auth_blueprint= Blueprint(AUTH_BLUEPRINT_NAME, __name__)

@auth_blueprint.route(LOGIN_ROUTE)
def login():
    redirect_uri = url_for('auth.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@auth_blueprint.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v1/userinfo', token=token)
    user = resp.json()
    session['user'] = user
    return redirect('/home')

@auth_blueprint.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/home')

@auth_blueprint.route(LOGIN_PAGE_ROUTE)
def login_page():
    return render_template(LOGIN_TEMPLATE)
