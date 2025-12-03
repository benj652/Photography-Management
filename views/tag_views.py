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

from flask import Blueprint, request
from constants import (
    DELETE,
    GET,
    MESSAGE_KEY,
    POST,
    PUT,
    TAG_ALL_ROUTE,
    TAG_CREATE_ROUTE,
    TAG_DEFAULT_NAME,
    TAG_DELETE_ROUTE,
    TAG_DELETE_SUCCESS_MESSAGE,
    TAG_GET_ONE_ROUTE,
    TAG_NAME,
    TAG_NAME_REQUIRED_MESSAGE,
    TAG_UPDATE_ROUTE,
    ERROR_BAD_REQUEST
)
from models import Tag, db
from utils import require_ta, require_approved

tags_blueprint = Blueprint(TAG_DEFAULT_NAME, __name__)


@tags_blueprint.route(TAG_ALL_ROUTE, methods=[GET])
@require_approved
def get_tags():
    """Return all tags as JSON-serializable dicts."""
    db_tags = Tag.query.all()
    return {TAG_DEFAULT_NAME: [t.to_dict() for t in db_tags]}


@tags_blueprint.route(TAG_GET_ONE_ROUTE, methods=[GET])
@require_ta
def get_tag(tag_id):
    """Return a single tag by ID as a dict."""
    db_tag = Tag.query.get_or_404(tag_id)
    return db_tag.to_dict()


@tags_blueprint.route(TAG_CREATE_ROUTE, methods=[POST])
@require_ta
def create_tag():
    """Create a new tag from JSON body and return the created tag."""
    data = request.get_json()
    name = data.get(TAG_NAME)
    if not name:
        return {MESSAGE_KEY: TAG_NAME_REQUIRED_MESSAGE}, ERROR_BAD_REQUEST
    new_tag = Tag(name=name)
    db.session.add(new_tag)
    db.session.commit()
    return new_tag.to_dict()


@tags_blueprint.route(TAG_UPDATE_ROUTE, methods=[PUT])
@require_ta
def update_tag(tag_id):
    """Update the tag's name and return the updated tag."""
    data = request.get_json()
    name = data.get(TAG_NAME)
    if not name:
        return {MESSAGE_KEY: TAG_NAME_REQUIRED_MESSAGE}, ERROR_BAD_REQUEST
    tag_to_update = Tag.query.get_or_404(tag_id)
    tag_to_update.name = name
    db.session.commit()
    return tag_to_update.to_dict()


@tags_blueprint.route(TAG_DELETE_ROUTE, methods=[DELETE])
@require_ta
def delete_tag(tag_id):
    """Delete the tag identified by ID and return a confirmation message."""
    tag_to_delete = Tag.query.get_or_404(tag_id)
    db.session.delete(tag_to_delete)
    db.session.commit()
    return {MESSAGE_KEY: TAG_DELETE_SUCCESS_MESSAGE}
