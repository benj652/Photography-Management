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

from flask import Blueprint, request
from flask_login import current_user, login_required
from datetime import datetime

from constants import (
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
from models import Consumable, Location, Tag, db
from utils.role_decorators import require_approved


consumables_blueprint = Blueprint(CONSUMABLES_DEFAULT_NAME, __name__)


@consumables_blueprint.route(CONSUMABLES_ALL_ROUTE, methods=[GET])
@login_required
@require_approved
def get_all_consumables():
    all_consumables = Consumable.query.all()
    return {
        CONSUMABLES_DEFAULT_NAME: [
            consumable.to_dict() for consumable in all_consumables
        ]
    }


@consumables_blueprint.route(CONSUMABLES_GET_ONE_ROUTE, methods=[GET])
@login_required
@require_approved
def get_consumable(consumable_id):
    consumable = Consumable.query.get_or_404(consumable_id)
    return consumable.to_dict()


@consumables_blueprint.route(CONSUMABLES_CREATE_ROUTE, methods=[POST])
@login_required
@require_approved
def create_consumable():
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

    location = None
    if location_id:
        location = Location.query.get(location_id)
        if not location:
            return {"error": "Location not found"}, 400

    new_consumable = Consumable(
        name=name,
        quantity=quantity,
        tags=tags,
        location=location,
        expires=expires,
        last_updated=datetime.now(),
        updated_by=current_user.id,
    )

    db.session.add(new_consumable)
    db.session.commit()

    return new_consumable.to_dict()


@consumables_blueprint.route(CONSUMABLES_UPDATE_ROUTE, methods=[PUT])
@login_required
@require_approved
def update_consumable(consumable_id):
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
    return consumable.to_dict()


@consumables_blueprint.route(CONSUMABLES_DELETE_ROUTE, methods=[DELETE])
@login_required
@require_approved
def delete_consumable(consumable_id):
    consumable = Consumable.query.get_or_404(consumable_id)
    db.session.delete(consumable)
    db.session.commit()
    return {"message": "Consumable deleted successfully"}