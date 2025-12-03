"""
=====================================================
 Camera Gear Routes (prefixed with "/camera_gear")
=====================================================

GET     /api/v1/camera_gear/all                → Retrieve all camera gear
GET     /api/v1/camera_gear/one/<int:gear_id>   → Retrieve a specific camera gear item by ID
POST    /api/v1/camera_gear/                   → Create a new camera gear item
PUT     /api/v1/camera_gear/<int:gear_id>       → Update an existing camera gear item
PUT     /api/v1/camera_gear/checkout/<int:gear_id> → Check out a camera gear item
PUT     /api/v1/camera_gear/checkin/<int:gear_id>  → Check in a camera gear item
DELETE  /api/v1/camera_gear/<int:gear_id>       → Delete a camera gear item by ID
"""

from datetime import datetime
from flask import Blueprint, request
from flask_login import current_user
from flask_login.utils import login_required

from constants import (
    CAMERA_GEAR_ALL_ROUTE,
    CAMERA_GEAR_CREATE_ROUTE,
    CAMERA_GEAR_DEAFULT_NAME,
    CAMERA_GEAR_DELETE_ROUTE,
    CAMERA_GEAR_GET_ONE_ROUTE,
    CAMERA_GEAR_CHECK_OUT_ROUTE,
    CAMERA_GEAR_CHECK_IN_ROUTE,
    CAMERA_GEAR_NAME_FIELD,
    CAMERA_GEAR_TAGS_FIELD,
    CAMERA_GEAR_UPDATE_ROUTE,
    DELETE,
    GET,
    POST,
    PUT,
)
from models import CameraGear, Location, Tag, db
from utils import require_ta, require_approved


camera_gear_blueprint = Blueprint(CAMERA_GEAR_DEAFULT_NAME, __name__)


@camera_gear_blueprint.route(CAMERA_GEAR_ALL_ROUTE, methods=[GET])
@login_required
@require_approved
def get_all_camera_gear():
    """Return all camera gear items as a list of dicts."""
    all_gear = CameraGear.query.all()
    return {CAMERA_GEAR_DEAFULT_NAME: [all_gear_item.to_dict() for all_gear_item in all_gear]}


@camera_gear_blueprint.route(CAMERA_GEAR_GET_ONE_ROUTE, methods=[GET])
@require_ta
@login_required
def get_camera_gear(gear_id):
    """Return a single camera gear item by ID."""
    gear_item = CameraGear.query.get_or_404(gear_id)
    return gear_item.to_dict()


@camera_gear_blueprint.route(CAMERA_GEAR_CREATE_ROUTE, methods=[POST])
@require_ta
@login_required
def create_camera_gear():
    """Create a new camera gear item from the provided JSON body."""
    data = request.get_json()
    name = data.get(CAMERA_GEAR_NAME_FIELD)
    tag_names = data.get(CAMERA_GEAR_TAGS_FIELD, [])
    location_id = data.get("location_id")

    if not name:
        return {"error": "Name is required"}, 400

    tags = []
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        tags.append(tag)

    new_gear = CameraGear(
        name=name,
        tags=tags,
        location_id=location_id,
        last_updated=datetime.now(),
        updated_by=current_user.id,
    )
    db.session.add(new_gear)
    db.session.commit()
    return new_gear.to_dict()


@camera_gear_blueprint.route(CAMERA_GEAR_UPDATE_ROUTE, methods=[PUT])
@require_ta
@login_required
def update_camera_gear(gear_id):
    """Update an existing camera gear item based on the provided JSON body."""
    gear_item = CameraGear.query.get_or_404(gear_id)
    data = request.get_json()
    name = data.get(CAMERA_GEAR_NAME_FIELD)
    tag_names = data.get(CAMERA_GEAR_TAGS_FIELD)
    location_id = data.get("location_id")

    if name:
        gear_item.name = name

    if tag_names is not None:
        tags = []
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        gear_item.tags = tags

    if location_id is not None:
        if location_id == "":
            gear_item.location_id = None
        else:
            location = Location.query.get(location_id)
            if location:
                gear_item.location_id = location_id
            else:
                return {"error": "Location not found"}, 404

    gear_item.last_updated = datetime.now()
    gear_item.updated_by = current_user.id

    db.session.commit()
    return gear_item.to_dict()


@camera_gear_blueprint.route(CAMERA_GEAR_CHECK_OUT_ROUTE, methods=[PUT])
@require_approved
@login_required
def check_out_camera_gear(gear_id):
    """Mark the specified camera gear item as checked out by current user."""
    gear_item = CameraGear.query.get_or_404(gear_id)
    if gear_item.checked_out_by is not None:
        return {"error": "Camera gear is already checked out"}, 400

    gear_item.checked_out_by = current_user.id
    gear_item.checked_out_date = datetime.now()
    gear_item.is_checked_out = True
    gear_item.last_updated = datetime.now()
    gear_item.updated_by = current_user.id

    db.session.commit()
    return gear_item.to_dict()


@camera_gear_blueprint.route(CAMERA_GEAR_CHECK_IN_ROUTE, methods=[PUT])
@require_approved
@login_required
def check_in_camera_gear(gear_id):
    """Mark the specified camera gear item as checked in (returned)."""
    gear_item = CameraGear.query.get_or_404(gear_id)
    if gear_item.checked_out_by is None:
        return {"error": "Camera gear is not checked out"}, 400

    gear_item.checked_out_by = None
    gear_item.checked_out_date = None
    gear_item.is_checked_out = False
    gear_item.return_date = datetime.now()
    gear_item.last_updated = datetime.now()
    gear_item.updated_by = current_user.id

    db.session.commit()
    return gear_item.to_dict()


@camera_gear_blueprint.route(CAMERA_GEAR_DELETE_ROUTE, methods=[DELETE])
@require_ta
@login_required
def delete_camera_gear(gear_id):
    """Delete the camera gear item identified by ID."""
    gear_item = CameraGear.query.get_or_404(gear_id)
    db.session.delete(gear_item)
    db.session.commit()
    return {"message": "Camera gear item deleted successfully."}
