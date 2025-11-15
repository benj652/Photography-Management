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

"""
=========================================
Flask route constants
=========================================
"""

"""
-----------------------------------------
API version
-----------------------------------------
"""
API_BASE = "/api/"
API_VERSION = "v1"
API_PREFIX = API_BASE + API_VERSION

"""
-----------------------------------------
CRUD operation routes
-----------------------------------------
"""
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"

"""
-----------------------------------------
Blueprint names
-----------------------------------------
"""
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

"""
===============================================
 Home Routes (prefixed with "/home") — Templates
===============================================

GET     /home/                     → Render the home page
GET     /home/unauthorized         → Render the unauthorized access page
GET     /home/lab-equipment        → Render the lab equipment page
GET     /home/camera-gear          → Render the camera gear page
REDIRECT home.home                 → Named route for "not found" fallback
"""
HOME_PREFIX = "/home"
HOME_ROUTE = "/"
NOT_FOUND_ROUTE = "home.home"
UNAUTHORIZED_ROUTE = "/unauthorized"
LAB_EQUIPMENT_ROUTE = "/lab-equipment"
CAMERA_GEAR_ROUTE = "/camera-gear"

# item routes
ITEM_PREFIX = "/items"
"""
=========================================constants
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


"""
=====================================================
 Camera Gear Routes (prefixed with "/camera_gear")
=====================================================

GET     /api/v1/camera_gear/all                → Retrieve all camera gear
GET     /api/v1/camera_gear/one/<int:tag_id>   → Retrieve a specific camera gear item by ID
POST    /api/v1/camera_gear/                   → Create a new camera gear item
PUT     /api/v1/camera_gear/<int:tag_id>       → Update an existing camera gear item
DELETE  /api/v1/camera_gear/<int:tag_id>       → Delete a camera gear item by ID
"""

CAMERA_GEAR_PREFIX = "/camera_gear"
CAMERA_GEAR_ALL_ROUTE = "/all"
CAMERA_GEAR_GET_ONE_ROUTE = "/one/<int:tag_id>"
CAMERA_GEAR_CREATE_ROUTE = "/"
CAMERA_GEAR_UPDATE_ROUTE = "/<int:tag_id>"
CAMERA_GEAR_DELETE_ROUTE = "/<int:tag_id>"

"""
=====================================================
    Camera Gear Fields
=====================================================
"""
CAMERA_GEAR_DEAFULT_NAME = "camera_gear"
CAMERA_GEAR_NAME_FIELD = "name"
CAMERA_GEAR_TAGS_FIELD = "tags"
CAMERA_GEAR_LOCATION_FIELD = "location_id"
CAMERA_GEAR_LAST_UPDATED_FIELD = "last_updated"
CAMERA_GEAR_UPDATED_BY_FIELD = "updated_by"
CAMERA_GEAR_IS_CHECKED_OUT_FIELD = "is_checked_out"
CAMERA_GEAR_CHECKED_OUT_BY_FIELD = "checked_out_by"
CAMERA_GEAR_CHECKED_OUT_DATE_FIELD = "checked_out_date"
CAMERA_GEAR_RETURN_DATE_FIELD = "return_date"

"""
=====================================================
 Lab equipment fields
=====================================================
"""
LAB_EQUIPMENT_DEFAULT_NAME = "lab_equipment"

LAB_EQUIPMENT_NAME_FIELD = "name"
LAB_EQUIPMENT_TAGS_FIELD = "tags"
LAB_EQUIPMENT_LAST_UPDATED_FIELD = "last_updated"
LAB_EQUIPMENT_UPDATED_BY_FIELD = "updated_by"
LAB_EQUIPMENT_LAST_SERVICED_ON_FIELD = "last_serviced_on"
LAB_EQUIPMENT_LAST_SERVICED_BY_FIELD = "last_serviced_by"
LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD = "service_frequency"
LAB_EQUIPMENT_UPDATED_BY_USER_FIELD = "updated_by_user"
LAB_EQUIPMENT_LAST_SERVICED_BY_USER_FIELD = "last_serviced_by_user"

"""
=====================================================
 Lab Equipment Routes (prefixed with "/lab_equipment")
=====================================================

GET     /api/v1/lab_equipment/all                → Retrieve all lab equipment
GET     /api/v1/lab_equipment/one/<int:tag_id>   → Retrieve a specific lab equipment item by ID
POST    /api/v1/lab_equipment/                   → Create a new lab equipment item
PUT     /api/v1/lab_equipment/<int:tag_id>       → Update an existing lab equipment item
DELETE  /api/v1/lab_equipment/<int:tag_id>       → Delete a lab equipment item by ID
"""

LAB_EQUIPMENT_PREFIX = "/lab_equipment"
LAB_EQUIPMENT_ALL_ROUTE = "/all"
LAB_EQUIPMENT_GET_ONE_ROUTE = "/one/<int:tag_id>"
LAB_EQUIPMENT_CREATE_ROUTE = "/"
LAB_EQUIPMENT_UPDATE_ROUTE = "/<int:tag_id>"
LAB_EQUIPMENT_DELETE_ROUTE = "/<int:tag_id>"

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

# Admin routes
ADMIN_PREFIX = "/admin"


"""
=========================================
Template constants
=========================================
"""
LOGIN_TEMPLATE = "landing.html"
HOME_TEMPLATE = "home.html"
UNAUTHORIZED_TEMPLATE = "unauthorized.html"
ADMIN_TEMPLATE = "admin.html"
CAMERA_GEAR_TEMPLATE = "camera_gear.html"
LAB_EQUIPMENT_TEMPLATE = "lab_equipment.html"

"""
=========================================
Environment variable names
=========================================
"""
GOOGLE_CLIENT_ID = "GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "GOOGLE_CLIENT_SECRET"
SECRET_KEY = "SECERET_KEY"
SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
SQLALCHEMY_TRACK_MODIFICATIONS = "SQLALCHEMY_TRACK_MODIFICATIONS"
DEFAULT_ADMIN_EMAIL = "DEFAULT_ADMIN_EMAIL"

"""
=========================================
Google constant variables
=========================================
"""
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


"""
=========================================
Session Keys
=========================================
"""
USER_KEY = "user"

"""
=========================================
JSON response keys
=========================================
"""
MESSAGE_KEY = "message"

"""
=========================================
Status messages
=========================================
"""
ERROR_NOT_FOUND = 404
ERROR_NOT_AUTHORIZED = 403
ERROR_BAD_REQUEST = 400
