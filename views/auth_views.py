"""
Auth views
"""

from flask import Blueprint, render_template, session, redirect, url_for
from constants import (
    AUTH_REDIRECT_URI,
    AUTHORIZE_ROUTE,
    CLIENT_KWARGS_ITEMS,
    CLIENT_KWARGS_KEY,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_USER_INFO_API,
    HOME_PREFIX,
    LOGIN_PAGE_ROUTE,
    LOGIN_ROUTE,
    LOGIN_TEMPLATE,
    AUTH_BLUEPRINT_NAME,
    LOGOUT_ROUTE,
    OAUTH_NAME,
    SERVER_METADATA_URL,
    USER_KEY,
)
from authlib.integrations.flask_client import OAuth
import os

oauth = OAuth()
google = None


def init_oauth(app):
    """Initialize OAuth and register Google provider."""
    global google
    oauth.init_app(app)

    google = oauth.register(
        name=OAUTH_NAME,
        server_metadata_url=SERVER_METADATA_URL,
        client_id=os.getenv(GOOGLE_CLIENT_ID),
        client_secret=os.getenv(GOOGLE_CLIENT_SECRET),
        client_kwargs={CLIENT_KWARGS_KEY: CLIENT_KWARGS_ITEMS},
    )


auth_blueprint = Blueprint(AUTH_BLUEPRINT_NAME, __name__)


@auth_blueprint.route(LOGIN_ROUTE)
def login():
    redirect_uri = url_for(AUTH_REDIRECT_URI, _external=True)
    return google.authorize_redirect(redirect_uri)


@auth_blueprint.route(AUTHORIZE_ROUTE)
def authorize():
    token = google.authorize_access_token()
    resp = google.get(GOOGLE_USER_INFO_API, token=token)
    user = resp.json()
    session[USER_KEY] = user
    return redirect(HOME_PREFIX)


@auth_blueprint.route(LOGOUT_ROUTE)
def logout():
    session.pop(USER_KEY, None)
    return redirect(USER_KEY)


@auth_blueprint.route(LOGIN_PAGE_ROUTE)
def login_page():
    return render_template(LOGIN_TEMPLATE)
