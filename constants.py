# Flask route constants

# CRUD operation routes
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"

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

# item routes
ITEM_PREFIX = "/items"

# item fields
ITEM_FIELD_NAME = "name"
ITEM_FIELD_QUANTITY = "quantity"
ITEM_FIELD_TAGS = "tags"
ITEM_FIELD_LOCATION_ID = "location_id"
ITEM_FIELD_EXPIRES = "expires"
ITEM_FIELD_UPDATED_BY = "updated_by"

# tags fields
TAG_PREFIX = "/tags"
TAG_ID = "id"
TAG_NAME = "name"
TAG_DEFAULT_NAME = "tags"
TAG_DELETE_SUCCESS_MESSAGE = "Tag deleted successfully"

"""
====================================
 Tag Routes (prefixed with "/tag")
====================================

GET     /tag/all                → Retrieve all tags
GET     /tag/one/<int:tag_id>   → Retrieve a specific tag by ID
POST    /tag/create             → Create a new tag
PUT     /tag/update/<int:tag_id>→ Update an existing tag
DELETE  /tag/delete/<int:tag_id>→ Delete a tag by ID
"""

TAG_ALL_ROUTE = "/all"
TAG_GET_ONE_ROUTE = "/one/<int:tag_id>"
TAG_CREATE_ROUTE = "/create"
TAG_UPDATE_ROUTE = "/update/<int:tag_id>"
TAG_DELETE_ROUTE = "/delete/<int:tag_id>"

# location fields
LOCATION_PREFIX = "/location"
LOCATION_ID = "id"
LOCATION_NAME = "name"
LOCATION_DEFAULT_NAME = "locations"

"""
=========================================
 Location Routes (prefixed with "/location")
=========================================

GET     /location/all                   → Retrieve all locations
GET     /location/one/<int:location_id> → Retrieve a specific location by ID
POST    /location/create                → Create a new location
PUT     /location/update/<int:location_id> → Update an existing location
DELETE  /location/delete/<int:location_id> → Delete a location by ID
"""


LOCATION_ALL_ROUTE = "/all"
LOCATION_GET_ONE_ROUTE = "/one/<int:location_id>"
LOCATION_CREATE_ROUTE = "/create"
LOCATION_UPDATE_ROUTE = "/update/<int:location_id>"
LOCATION_DELETE_ROUTE = "/delete/<int:location_id>"

LOCATION_DELETE_SUCCESS_MESSAGE = "location deleted successfully"

# Template constants
LOGIN_TEMPLATE = "landing.html"
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

# JSON response keys
MESSAGE_KEY = "message"
