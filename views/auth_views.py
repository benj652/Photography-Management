"""
=========================================================
 Authentication Routes (prefixed with "/auth")
=========================================================

GET     /auth/                     → Login page
POST    /auth/login                → Handle login submission
GET     /auth/logout               → Log the user out
GET     /auth/authorize            → OAuth2 / SSO authorization endpoint
REDIRECT auth.authorize            → Internal redirect URI name
"""

from flask import Blueprint, json, render_template, session, redirect, url_for
from constants import (
    AUTH_PREFIX,
    AUTH_REDIRECT_URI,
    AUTHORIZE_ROUTE,
    CLIENT_KWARGS_ITEMS,
    CLIENT_KWARGS_KEY,
    DEFAULT_ADMIN_EMAIL,
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_USER_EMAIL,
    GOOGLE_USER_FAMILY_NAME,
    GOOGLE_USER_GIVEN_NAME,
    GOOGLE_USER_INFO_API,
    GOOGLE_USER_PICTURE,
    HOME_PREFIX,
    LOGIN_PAGE_ROUTE,
    LOGIN_ROUTE,
    LOGIN_TEMPLATE,
    AUTH_BLUEPRINT_NAME,
    LOGOUT_ROUTE,
    OAUTH_NAME,
    SERVER_METADATA_URL,
    USER_KEY,
    UserRole,
)
from authlib.integrations.flask_client import OAuth
import os
from flask_login import login_required, login_user, logout_user
from models import User, db

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
    """
    Authorize user and fetch user info from Google

    the user item is in the following format:
    {
        'id': '114544450990536914219',
        'email': 'bmjaff26@colby.edu',
        'verified_email': True,
        'name': 'Benjamin Jaffe',
        'given_name': 'Benjamin',
        'family_name': 'Jaffe',
        'picture': 'https://lh3.googleusercontent.com/a/ACg8ocJwc-igE1-1TWV732HsBwAAu8kC9JpfbLsPOGVQD1aO2Cp_9w=s96-c',
        'hd': 'colby.edu'
    }
    """
    token = google.authorize_access_token()
    resp = google.get(GOOGLE_USER_INFO_API, token=token)
    google_user = resp.json()

    app_user = get_user(google_user[GOOGLE_USER_EMAIL])
    if not app_user:
        app_user = create_new_user(google_user)

    login_user(app_user)
    session[USER_KEY] = app_user.id
    return redirect(HOME_PREFIX)


@auth_blueprint.route(LOGOUT_ROUTE)
@login_required
def logout():
    session.pop(USER_KEY, None)
    logout_user()
    return redirect(AUTH_PREFIX)


@auth_blueprint.route(LOGIN_PAGE_ROUTE)
def login_page():
    return render_template(LOGIN_TEMPLATE)


def create_new_user(user):
    """
    This function exists so in the future, when we add roles and stuff
    we will add the roles here.
    """
    # print(user[GOOGLE_USER_EMAIL])
    # print(os.getenv(DEFAULT_ADMIN_EMAIL))
    starting_role = UserRole.INVALID

    if user[GOOGLE_USER_EMAIL] == os.getenv(DEFAULT_ADMIN_EMAIL):
        starting_role = UserRole.ADMIN
    # print(starting_role)

    new_user = User(
        email=user[GOOGLE_USER_EMAIL],
        first_name=user[GOOGLE_USER_GIVEN_NAME],
        last_name=user[GOOGLE_USER_FAMILY_NAME],
        profile_picture=user[GOOGLE_USER_PICTURE],
        role=starting_role,  # Temporary role assignment
    )
    db.session.add(new_user)
    db.session.commit()
    return new_user


def get_user(email):
    """
    Checks for existing user by email, if found return said user, else return None
    """
    existing_user = User.query.filter_by(email=email).first()
    return existing_user
