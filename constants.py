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
NOT_FOUND_ROUTE = "home.home"

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

"""
From the user object returned from google
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
GOOGLE_USER_ID = "id"
GOOGLE_USER_EMAIL = "email"
GOOGLE_USER_VERIFIED_EMAIL = "verified_email"
GOOGLE_USER_NAME = "name"
GOOGLE_USER_GIVEN_NAME = "given_name"
GOOGLE_USER_FAMILY_NAME = "family_name"
GOOGLE_USER_PICTURE = "picture"
GOOGLE_USER_HD = "hd"


# Session keys
USER_KEY = "user"
