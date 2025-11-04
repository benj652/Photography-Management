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

from constants import (
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
from flask import Blueprint, request
from flask_login import login_required
from models import Location, db

location_blueprint = Blueprint(LOCATION_DEFAULT_NAME, __name__)


@location_blueprint.route(LOCATION_ALL_ROUTE, methods=[GET])
@login_required
def get_locations():
    locations = Location.query.all()
    return {LOCATION_DEFAULT_NAME: [loc.to_dict() for loc in locations]}


@location_blueprint.route(LOCATION_GET_ONE_ROUTE, methods=[GET])
@login_required
def get_location(location_id):
    location = Location.query.get_or_404(location_id)
    return location.to_dict()


@location_blueprint.route(LOCATION_CREATE_ROUTE, methods=[POST])
@login_required
def create_location():
    data = request.get_json()
    name = data.get(LOCATION_NAME)
    if not name:
        return {MESSAGE_KEY: LOCATION_NAME_NEEDED_MESSAGE}, ERROR_BAD_REQUEST 
    new_location = Location(name=name)
    db.session.add(new_location)
    db.session.commit()
    return new_location.to_dict()


@location_blueprint.route(LOCATION_CREATE_ROUTE, methods=[PUT])
@login_required
def update_location(location_id):
    data = request.get_json()
    name = data.get(LOCATION_NAME)
    if not name:
        return {MESSAGE_KEY: LOCATION_NAME_NEEDED_MESSAGE}, ERROR_BAD_REQUEST 
    location = Location.query.get_or_404(location_id)
    location.name = name
    db.session.commit()
    return location.to_dict()


@location_blueprint.route(LOCATION_DELETE_ROUTE, methods=[DELETE])
@login_required
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    db.session.delete(location)
    db.session.commit()
    return {MESSAGE_KEY: LOCATION_DELETE_SUCCESS_MESSAGE}
