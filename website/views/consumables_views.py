"""
=====================================================
 Consumables Routes (prefixed with "/consumables")
=====================================================

GET     /api/v1/consumables/all                → Retrieve all consumables
GET     /api/v1/consumables/one/<int:consumable_id>   → Retrieve a specific consumable by ID
POST    /api/v1/consumables/                   → Create a new consumable
PUT     /api/v1/consumables/<int:consumable_id>       → Update an existing consumable
DELETE  /api/v1/consumables/<int:consumable_id>       → Delete a consumable by ID
"""

from datetime import datetime
from flask import Blueprint, request
from flask_login import current_user
from ..constants import (
    DELETE,
    GET,
    POST,
    PUT,
    CONSUMABLES_ALL_ROUTE,
    CONSUMABLES_CREATE_ROUTE,
    CONSUMABLES_DEFAULT_NAME,
    CONSUMABLES_DELETE_ROUTE,
    CONSUMABLES_GET_ONE_ROUTE,
    CONSUMABLES_UPDATE_ROUTE,
    ITEM_FIELD_NAME,
    ITEM_FIELD_QUANTITY,
    ITEM_FIELD_TAGS,
    ITEM_FIELD_LOCATION_ID,
    ITEM_FIELD_EXPIRES,
)
from ..models import Consumable, Location, Tag
from ..utils import (
    require_approved,
    require_ta,
    send_low_stock_alert
)

from website import db

consumables_blueprint = Blueprint(CONSUMABLES_DEFAULT_NAME, __name__)


@consumables_blueprint.route(CONSUMABLES_ALL_ROUTE, methods=[GET])
@require_approved
def get_all_consumables():
    """Return all consumable items as JSON-serializable dicts."""
    all_consumables = Consumable.query.all()
    return {CONSUMABLES_DEFAULT_NAME: [consumable.to_dict() for consumable in all_consumables]}


@consumables_blueprint.route(CONSUMABLES_GET_ONE_ROUTE, methods=[GET])
@require_ta
def get_consumable(consumable_id):
    """Return a single consumable item by ID."""
    consumable = Consumable.query.get_or_404(consumable_id)
    return consumable.to_dict()


@consumables_blueprint.route(CONSUMABLES_CREATE_ROUTE, methods=[POST])
@require_ta
def create_consumable():
    """Create a consumable from JSON body and return the created object."""
    data = request.get_json()
    name = data.get(ITEM_FIELD_NAME)
    quantity = data.get(ITEM_FIELD_QUANTITY, 1)
    tag_names = data.get(ITEM_FIELD_TAGS, [])
    location_id = data.get(ITEM_FIELD_LOCATION_ID)
    expires_str = data.get(ITEM_FIELD_EXPIRES)

    if not name:
        return {"error": "Name is required"}, 400

    expires = None
    if expires_str:
        try:
            expires = datetime.fromisoformat(expires_str).date()
        except ValueError:
            return {"error": "Invalid expiration date format"}, 400

    tags = []
    for tag_name in tag_names:
        tag = Tag.query.filter_by(name=tag_name).first()
        if not tag:
            tag = Tag(name=tag_name)
            db.session.add(tag)
        tags.append(tag)

    # Ensure tags are unique by name to avoid duplicate many-to-many inserts
    seen_names = set()
    unique_tags = []
    for t in tags:
        if getattr(t, "name", None) and t.name not in seen_names:
            seen_names.add(t.name)
            unique_tags.append(t)
    tags = unique_tags

    location = None
    if location_id:
        location = Location.query.get(location_id)
        if not location:
            return {"error": "Location not found"}, 400

    # Create the consumable first without tags to avoid potential duplicate
    # many-to-many association inserts when both sides are transient. After
    # the consumable has a primary key, assign tags and commit again.
    new_consumable = Consumable(
        name=name,
        quantity=quantity,
        location=location,
        expires=expires,
        last_updated=datetime.now(),
        updated_by=current_user.id,
    )

    db.session.add(new_consumable)
    db.session.commit()

    if tags:
        new_consumable.tags = tags
        db.session.commit()

    # After creating, check for low stock and notify admins if configured
    try:
        send_low_stock_alert(new_consumable)
    except Exception:
        # do not break the create flow if email sending fails
        pass

    return new_consumable.to_dict()


@consumables_blueprint.route(CONSUMABLES_UPDATE_ROUTE, methods=[PUT])
@require_ta
def update_consumable(consumable_id):
    """Update an existing consumable with the provided JSON fields."""
    consumable = Consumable.query.get_or_404(consumable_id)
    data = request.get_json()
    name = data.get(ITEM_FIELD_NAME)
    quantity = data.get(ITEM_FIELD_QUANTITY)
    tag_names = data.get(ITEM_FIELD_TAGS)
    location_id = data.get(ITEM_FIELD_LOCATION_ID)
    expires_str = data.get(ITEM_FIELD_EXPIRES)

    if name:
        consumable.name = name

    if quantity is not None:
        consumable.quantity = quantity

    if expires_str is not None:
        if expires_str:
            try:
                consumable.expires = datetime.fromisoformat(expires_str).date()
            except ValueError:
                return {"error": "Invalid expiration date format"}, 400
        else:
            consumable.expires = None

    if tag_names is not None:
        tags = []
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        consumable.tags = tags

    if ITEM_FIELD_LOCATION_ID in data:
        if location_id:
            location = Location.query.get(location_id)
            if not location:
                return {"error": "Location not found"}, 400
            consumable.location = location
        else:
            consumable.location = None

    consumable.last_updated = datetime.now()
    consumable.updated_by = current_user.id

    db.session.commit()

    # After updating, check for low stock and notify admins if configured
    try:
        send_low_stock_alert(consumable)
    except Exception:
        # do not break the update flow if email sending fails
        pass

    return consumable.to_dict()


@consumables_blueprint.route(CONSUMABLES_DELETE_ROUTE, methods=[DELETE])
@require_ta
def delete_consumable(consumable_id):
    """Delete the specified consumable and return a confirmation message."""
    consumable = Consumable.query.get_or_404(consumable_id)
    db.session.delete(consumable)
    db.session.commit()
    return {"message": "Consumable deleted successfully"}
