# Flask route constants

# API version
API_BASE = "/api/"
API_VERSION = "v1"
API_PREFIX = API_BASE + API_VERSION

# CRUD operation routes
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"

# Blueprint names
AUTH_BLUEPRINT_NAME = "auth"
HOME_BLUEPRINT_NAME = "home"

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
"""
=========================================
 Item Routes (prefixed with "/item")
=========================================

GET     /api/v1/items/all                   → Retrieve all items
GET     /api/v1/items/one/<int:item_id>     → Retrieve a specific item by ID
POST    /api/v1/items/                      → Create a new item
PUT     /api/v1/items/<int:item_id>         → Update an existing item
DELETE  /api/v1/items/<int:item_id>         → Delete an item by ID
"""

ITEM_ALL_ROUTE = "/all"
ITEM_GET_ONE_ROUTE = "/one/<int:item_id>"
ITEM_CREATE_ROUTE = "/"
ITEM_UPDATE_ROUTE = "/<int:item_id>"
ITEM_DELETE_ROUTE = "/<int:item_id>"

ITEM_NAME_NEEDED_MESSAGE = "Item name is required."

# item fields
ITEM_FIELD_ID = "id"
ITEM_FIELD_NAME = "name"
ITEM_FIELD_QUANTITY = "quantity"
ITEM_FIELD_TAGS = "tags"
ITEM_FIELD_LOCATION_ID = "location_id"
ITEM_FIELD_EXPIRES = "expires"
ITEM_FIELD_LAST_UPDATED = "last_updated"
ITEM_FIELD_UPDATED_BY = "updated_by"

# tags fields
TAG_PREFIX = "/tags"
TAG_ID = "id"
TAG_NAME = "name"
TAG_DEFAULT_NAME = "tags"
TAG_DELETE_SUCCESS_MESSAGE = "Tag deleted successfully"
TAG_NAME_REQUIRED_MESSAGE = "Tag name is required."

"""
====================================
 Tag Routes (prefixed with "/tag")
====================================

GET     /api/v1/tag/all                → Retrieve all tags
GET     /api/v1/tag/one/<int:tag_id>   → Retrieve a specific tag by ID
POST    /api/v1/tag/                   → Create a new tag
PUT     /api/v1/tag/<int:tag_id>       → Update an existing tag
DELETE  /api/v1/tag/<int:tag_id>       → Delete a tag by ID
"""

TAG_ALL_ROUTE = "/all"
TAG_GET_ONE_ROUTE = "/one/<int:tag_id>"
TAG_CREATE_ROUTE = "/"
TAG_UPDATE_ROUTE = "/<int:tag_id>"
TAG_DELETE_ROUTE = "/<int:tag_id>"

# location fields
LOCATION_PREFIX = "/location"
LOCATION_ID = "id"
LOCATION_NAME = "name"
LOCATION_DEFAULT_NAME = "locations"

"""
=========================================
 Location Routes (prefixed with "/location")
=========================================

GET     /api/v1/location/all                   → Retrieve all locations
GET     /api/v1/location/one/<int:location_id> → Retrieve a specific location by ID
POST    /api/v1/location/                      → Create a new location
PUT     /api/v1/location/<int:location_id>     → Update an existing location
DELETE  /api/v1/location/<int:location_id>     → Delete a location by ID
"""


LOCATION_ALL_ROUTE = "/all"
LOCATION_GET_ONE_ROUTE = "/one/<int:location_id>"
LOCATION_CREATE_ROUTE = "/"
LOCATION_UPDATE_ROUTE = "/<int:location_id>"
LOCATION_DELETE_ROUTE = "/<int:location_id>"

LOCATION_DELETE_SUCCESS_MESSAGE = "location deleted successfully"
LOCATION_NAME_NEEDED_MESSAGE = "location name is required."


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

# Status messages
ERROR_NOT_FOUND = 404
ERROR_NOT_AUTHORIZED = 403
ERROR_BAD_REQUEST = 400
