import enum

"""
=========================================
Standard user enum for roles.
=========================================

ADMIN: Below permissions and Has full access to all resources and can manage other users.
TA: Below permissions Can view and modify resources but cannot manage users.
STUDENT: Below permissions can only view resources and check out equipment.
INVALID: Student not in Photography who can not see or edit the database at all.
"""

class UserRole(enum.Enum):
    ADMIN = "admin"
    TA = "ta"
    STUDENT = "student"
    INVALID = "invalid"

# Flask route constants

# CRUD operation routes
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"

# Blueprint names
AUTH_BLUEPRINT_NAME = "auth"
HOME_BLUEPRINT_NAME = "home"

# Auth routes
AUTH_PREFIX = "/auth"
LOGIN_PAGE_ROUTE = "/"
LOGIN_ROUTE = "/login"
LOGOUT_ROUTE = "/logout"
AUTHORIZE_ROUTE = "/authorize"
AUTH_REDIRECT_URI = "auth.authorize"

# home routes
HOME_PREFIX = "/home"
HOME_ROUTE = "/"
NOT_FOUND_ROUTE = "home.home"
UNAUTHORIZED_ROUTE = "/unauthorized"

# item routes
ITEM_PREFIX = "/items"
"""
=========================================
 Item Routes (prefixed with "/item")
=========================================

GET     /items/all                   → Retrieve all items
GET     /items/one/<int:item_id>     → Retrieve a specific item by ID
POST    /items/create                → Create a new item
PUT     /items/update/<int:item_id>  → Update an existing item
DELETE  /items/delete/<int:item_id>  → Delete an item by ID
"""

ITEM_ALL_ROUTE = "/all"
ITEM_GET_ONE_ROUTE = "/one/<int:item_id>"
ITEM_CREATE_ROUTE = "/create"
ITEM_UPDATE_ROUTE = "/update/<int:item_id>"
ITEM_DELETE_ROUTE = "/delete/<int:item_id>"

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
LOCATION_NAME_NEEDED_MESSAGE = "location name is required."


# Template constants
LOGIN_TEMPLATE = "landing.html"
HOME_TEMPLATE = "home.html"
UNAUTHORIZED_TEMPLATE = "unauthorized.html"

# environment variable names
GOOGLE_CLIENT_ID = "GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "GOOGLE_CLIENT_SECRET"
SECRET_KEY = "SECERET_KEY"
SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
SQLALCHEMY_TRACK_MODIFICATIONS = "SQLALCHEMY_TRACK_MODIFICATIONS"
DEFAULT_ADMIN_EMAIL = "DEFAULT_ADMIN_EMAIL"

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
