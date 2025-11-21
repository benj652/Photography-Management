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

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Item, Tag, Location
from sqlalchemy.orm import joinedload
from datetime import datetime
from constants import (
    DELETE,
    ERROR_BAD_REQUEST,
    GET,
    ITEM_PREFIX,
    ITEM_ALL_ROUTE,
    ITEM_CREATE_ROUTE,
    ITEM_DELETE_ROUTE,
    ITEM_FIELD_EXPIRES,
    ITEM_FIELD_LOCATION_ID,
    ITEM_FIELD_NAME,
    ITEM_FIELD_QUANTITY,
    ITEM_FIELD_TAGS,
    ITEM_FIELD_UPDATED_BY,
    ITEM_GET_ONE_ROUTE,
    ITEM_NAME_NEEDED_MESSAGE,
    ITEM_UPDATE_ROUTE,
    MESSAGE_KEY,
    POST,
    PUT,
)

item_blueprint = Blueprint(ITEM_PREFIX, __name__)


@item_blueprint.route(ITEM_ALL_ROUTE, methods=[GET])
@login_required
def get_all_items():
    items = Item.query.all()

    return jsonify(items=[item.to_dict() for item in items])


@item_blueprint.route(ITEM_GET_ONE_ROUTE, methods=[GET])
@login_required
def get_item(item_id):
    item = Item.query.options(
        joinedload(Item.tags),
        joinedload(Item.location),
        joinedload(Item.updated_by_user),
    ).get_or_404(item_id)

    item_dict = {
        ITEM_FIELD_NAME: item.name,
        ITEM_FIELD_QUANTITY: item.quantity,
        ITEM_FIELD_TAGS: [tag.name for tag in item.tags],
        ITEM_FIELD_LOCATION_ID: item.location.name if item.location else None,
        ITEM_FIELD_EXPIRES: item.expires.isoformat() if item.expires else None,
        ITEM_FIELD_UPDATED_BY: (
            item.updated_by_user.email if item.updated_by_user else None
        ),
    }

    return jsonify(item_dict)


@item_blueprint.route(ITEM_CREATE_ROUTE, methods=[POST])
@login_required
def create_item():
    data = request.get_json()
    name = data.get(ITEM_FIELD_NAME)
    quantity = data.get(ITEM_FIELD_QUANTITY, 1)
    tag_names = data.get(ITEM_FIELD_TAGS, [])
    location_id = data.get(ITEM_FIELD_LOCATION_ID)
    expires_str = data.get(ITEM_FIELD_EXPIRES)

    if not name:
        return {MESSAGE_KEY: ITEM_NAME_NEEDED_MESSAGE}, ERROR_BAD_REQUEST

    expires = None
    if expires_str:
        try:
            expires = datetime.fromisoformat(expires_str)
        except ValueError:
            return "Invalid expiration date format", 400

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
            return "Location not found", 400

    new_item = Item(
        name=name,
        quantity=quantity,
        tags=tags,
        location=location,
        expires=expires,
        last_updated=datetime.now(),  # Fix: Set the current datetime
        updated_by=current_user.id,  # Fix: Set the user ID instead of user object
    )

    db.session.add(new_item)
    db.session.commit()

    return new_item.to_dict(), 201


@item_blueprint.route(ITEM_UPDATE_ROUTE, methods=[PUT])
@login_required
def update_item(item_id):
    data = request.get_json()
    name = data.get(ITEM_FIELD_NAME)
    quantity = data.get(ITEM_FIELD_QUANTITY)
    tag_names = data.get(ITEM_FIELD_TAGS) if ITEM_FIELD_TAGS in data else None
    location_id = (
        data.get(ITEM_FIELD_LOCATION_ID) if ITEM_FIELD_LOCATION_ID in data else None
    )
    expires_str = data.get(ITEM_FIELD_EXPIRES)

    item = Item.query.get_or_404(item_id)

    if name:
        item.name = name
    if quantity is not None:
        item.quantity = quantity
    if expires_str:
        try:
            item.expires = datetime.fromisoformat(expires_str)
        except ValueError:
            return "Invalid expiration date format", 400
    if tag_names is not None:
        tags = []
        for tag_name in tag_names or []:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        item.tags = tags

    if ITEM_FIELD_LOCATION_ID in data:
        if location_id:
            location = Location.query.get(location_id)
            if not location:
                return "Location not found", 400
            item.location = location
        else:
            item.location = None

    db.session.commit()
    return item.to_dict()


@item_blueprint.route(ITEM_DELETE_ROUTE, methods=[DELETE])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return {MESSAGE_KEY: "Item deleted successfully"}
