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

from flask import Blueprint, request
from ..constants import (
    DELETE,
    ERROR_BAD_REQUEST,
    GET,
    LOCATION_ALL_ROUTE,
    LOCATION_CREATE_ROUTE,
    LOCATION_DEFAULT_NAME,
    LOCATION_DELETE_ROUTE,
    LOCATION_DELETE_SUCCESS_MESSAGE,
    LOCATION_GET_ONE_ROUTE,
    LOCATION_NAME,
    LOCATION_NAME_NEEDED_MESSAGE,
    MESSAGE_KEY,
    POST,
    PUT,
)
from ..models import Location
from website import db
from ..utils import require_approved, require_ta

location_blueprint = Blueprint(LOCATION_DEFAULT_NAME, __name__)


@location_blueprint.route(LOCATION_ALL_ROUTE, methods=[GET])
@require_approved
def get_locations():
    """Return all locations as a list of dicts."""
    locations = Location.query.all()
    return {LOCATION_DEFAULT_NAME: [loc.to_dict() for loc in locations]}


@location_blueprint.route(LOCATION_GET_ONE_ROUTE, methods=[GET])
@require_ta
def get_location(location_id):
    """Return a location by ID as a dict."""
    location = Location.query.get_or_404(location_id)
    return location.to_dict()


@location_blueprint.route(LOCATION_CREATE_ROUTE, methods=[POST])
@require_ta
def create_location():
    """Create a new location from the JSON body and return it."""
    data = request.get_json()
    name = data.get(LOCATION_NAME)
    if not name:
        return {MESSAGE_KEY: LOCATION_NAME_NEEDED_MESSAGE}, ERROR_BAD_REQUEST
    new_location = Location(name=name)
    db.session.add(new_location)
    db.session.commit()
    return new_location.to_dict()


@location_blueprint.route(LOCATION_CREATE_ROUTE, methods=[PUT])
@require_ta
def update_location(location_id):
    """Update the name of an existing location and return it."""
    data = request.get_json()
    name = data.get(LOCATION_NAME)
    if not name:
        return {MESSAGE_KEY: LOCATION_NAME_NEEDED_MESSAGE}, ERROR_BAD_REQUEST
    location = Location.query.get_or_404(location_id)
    location.name = name
    db.session.commit()
    return location.to_dict()


@location_blueprint.route(LOCATION_DELETE_ROUTE, methods=[DELETE])
@require_ta
def delete_location(location_id):
    """Delete the location with the given ID and return a confirmation."""
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    return {MESSAGE_KEY: LOCATION_DELETE_SUCCESS_MESSAGE}
