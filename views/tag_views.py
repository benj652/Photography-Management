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

from flask_login import login_required
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
    TAG_UPDATE_ROUTE,
)
from models import Tag, db

tags_blueprint = Blueprint(TAG_DEFAULT_NAME, __name__)


@tags_blueprint.route(TAG_ALL_ROUTE, methods=[GET])
@login_required
def get_tags():
    db_tags = Tag.query.all()
    return {TAG_DEFAULT_NAME: [t.to_dict() for t in db_tags]}


@tags_blueprint.route(TAG_GET_ONE_ROUTE, methods=[GET])
@login_required
def get_tag(tag_id):
    db_tag = Tag.query.get_or_404(tag_id)
    return db_tag.to_dict()


@tags_blueprint.route(TAG_CREATE_ROUTE, methods=[POST])
@login_required
def create_tag():
    data = request.get_json()
    name = data.get(TAG_NAME)
    new_tag = Tag(name=name)
    db.session.add(new_tag)
    db.session.commit()
    return new_tag.to_dict()


@tags_blueprint.route(TAG_UPDATE_ROUTE, methods=[PUT])
@login_required
def update_tag(tag_id):
    data = request.get_json()
    tag_to_update = Tag.query.get_or_404(tag_id)
    tag_to_update.name = data.get(TAG_NAME)
    db.session.commit()
    return tag_to_update.to_dict()


@tags_blueprint.route(TAG_DELETE_ROUTE, methods=[DELETE])
@login_required
def delete_tag(tag_id):
    tag_to_delete = Tag.query.get_or_404(tag_id)
    db.session.delete(tag_to_delete)
    db.session.commit()
    return {MESSAGE_KEY: TAG_DELETE_SUCCESS_MESSAGE}
