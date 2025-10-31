# Flask route constants

# Blueprint names
AUTH_BLUEPRINT_NAME = "auth"

# Auth routes
AUTH_PREFIX = "/auth"
LOGIN_PAGE_ROUTE = "/"
LOGIN_ROUTE = "/login"
LOGOUT_ROUTE = "/logout"
AUTHORIZE_ROUTE = "/authorize"
AUTH_REDIRECT_URI = "auth.authorize"

# home routes
HOME_PREFIX = "/home"

# Template constants
LOGIN_TEMPLATE = "login.html"
HOME_TEMPLATE = "home.html"

# environment variable names
GOOGLE_CLIENT_ID = "GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "GOOGLE_CLIENT_SECRET"
SECRET_KEY = "SECERET_KEY"
SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
SQLALCHEMY_TRACK_MODIFICATIONS = "SQLALCHEMY_TRACK_MODIFICATIONS"

# Google constant variables
OAUTH_NAME = "google"
SERVER_METADATA_URL = "https://accounts.google.com/.well-known/openid-configuration"
CLIENT_KWARGS_KEY = "scope"
CLIENT_KWARGS_ITEMS = "openid email profile"
GOOGLE_USER_INFO_API = "https://www.googleapis.com/oauth2/v1/userinfo"


# Session keys
USER_KEY = "user"
