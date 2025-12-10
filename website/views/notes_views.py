"""
=====================================================
 Notes Routes (prefixed with "/notes")
=====================================================

GET     /api/v1/notes/all                → Retrieve all notes
GET     /api/v1/notes/one/<int:note_id>  → Retrieve a specific note by ID
GET     /api/v1/notes/by-item/<item_type>/<int:item_id> → Retrieve note for a specific item
POST    /api/v1/notes/                   → Create a new note
PUT     /api/v1/notes/<int:note_id>      → Update an existing note
DELETE  /api/v1/notes/<int:note_id>      → Delete a note by ID
"""

from datetime import datetime
from flask import Blueprint, request
from flask_login import current_user
from flask_login.utils import login_required

from ..constants import (
    DELETE,
    GET,
    POST,
    PUT,
    NOTES_ALL_ROUTE,
    NOTES_CREATE_ROUTE,
    NOTES_DEFAULT_NAME,
    NOTES_DELETE_ROUTE,
    NOTES_GET_ONE_ROUTE,
    NOTES_BY_ITEM_ROUTE,
    NOTES_UPDATE_ROUTE,
    NOTE_CONTENT_FIELD,
    NOTE_ITEM_TYPE_FIELD,
    NOTE_ITEM_ID_FIELD,
    NOTE_CONTENT_REQUIRED_MESSAGE,
    NOTE_ITEM_TYPE_REQUIRED_MESSAGE,
    NOTE_ITEM_ID_REQUIRED_MESSAGE,
    NOTE_DELETE_SUCCESS_MESSAGE,
    ERROR_BAD_REQUEST,
)
from ..models import Note, CameraGear, LabEquipment, Consumable
from ..utils import require_ta, require_approved

from website import db


notes_blueprint = Blueprint(NOTES_DEFAULT_NAME, __name__)


@notes_blueprint.route(NOTES_ALL_ROUTE, methods=[GET])
@login_required
@require_approved
def get_all_notes():
    """Return all notes as a list of dicts."""
    all_notes = Note.query.all()
    return {NOTES_DEFAULT_NAME: [note.to_dict() for note in all_notes]}


@notes_blueprint.route(NOTES_GET_ONE_ROUTE, methods=[GET])
@require_approved
@login_required
def get_note(note_id):
    """Return a single note by ID."""
    note = Note.query.get_or_404(note_id)
    return note.to_dict()


@notes_blueprint.route(NOTES_BY_ITEM_ROUTE, methods=[GET])
@login_required
@require_approved
def get_note_by_item(item_type, item_id):
    """Return the note for a specific item, or None if no note exists."""
    note = None
    
    if item_type == "camera_gear":
        note = Note.query.filter_by(camera_gear_id=item_id).first()
    elif item_type == "lab_equipment":
        note = Note.query.filter_by(lab_equipment_id=item_id).first()
    elif item_type == "consumable":
        note = Note.query.filter_by(consumable_id=item_id).first()
    else:
        return {"error": f"Invalid item type: {item_type}"}, ERROR_BAD_REQUEST
    
    if note:
        return note.to_dict()
    return {}


@notes_blueprint.route(NOTES_CREATE_ROUTE, methods=[POST])
@require_approved
@login_required
def create_note():
    """Create a new note for an item from the provided JSON body."""
    data = request.get_json()
    content = data.get(NOTE_CONTENT_FIELD)
    item_type = data.get(NOTE_ITEM_TYPE_FIELD)
    item_id = data.get(NOTE_ITEM_ID_FIELD)

    if not content:
        return {"error": NOTE_CONTENT_REQUIRED_MESSAGE}, ERROR_BAD_REQUEST
    
    if not item_type:
        return {"error": NOTE_ITEM_TYPE_REQUIRED_MESSAGE}, ERROR_BAD_REQUEST
    
    if item_id is None:
        return {"error": NOTE_ITEM_ID_REQUIRED_MESSAGE}, ERROR_BAD_REQUEST

    # Validate item type and check if item exists
    camera_gear_id = None
    lab_equipment_id = None
    consumable_id = None

    if item_type == "camera_gear":
        item = CameraGear.query.get(item_id)
        if not item:
            return {"error": "Camera gear item not found"}, ERROR_BAD_REQUEST
        camera_gear_id = item_id
        # Check if note already exists for this item
        existing_note = Note.query.filter_by(camera_gear_id=item_id).first()
        if existing_note:
            return {"error": "A note already exists for this camera gear item"}, ERROR_BAD_REQUEST
    elif item_type == "lab_equipment":
        item = LabEquipment.query.get(item_id)
        if not item:
            return {"error": "Lab equipment item not found"}, ERROR_BAD_REQUEST
        lab_equipment_id = item_id
        # Check if note already exists for this item
        existing_note = Note.query.filter_by(lab_equipment_id=item_id).first()
        if existing_note:
            return {"error": "A note already exists for this lab equipment item"}, ERROR_BAD_REQUEST
    elif item_type == "consumable":
        item = Consumable.query.get(item_id)
        if not item:
            return {"error": "Consumable item not found"}, ERROR_BAD_REQUEST
        consumable_id = item_id
        # Check if note already exists for this item
        existing_note = Note.query.filter_by(consumable_id=item_id).first()
        if existing_note:
            return {"error": "A note already exists for this consumable item"}, ERROR_BAD_REQUEST
    else:
        return {"error": f"Invalid item type: {item_type}. Must be 'camera_gear', 'lab_equipment', or 'consumable'"}, ERROR_BAD_REQUEST

    new_note = Note(
        content=content,
        camera_gear_id=camera_gear_id,
        lab_equipment_id=lab_equipment_id,
        consumable_id=consumable_id,
        created_by=current_user.id,
    )

    db.session.add(new_note)
    db.session.commit()
    return new_note.to_dict()


@notes_blueprint.route(NOTES_UPDATE_ROUTE, methods=[PUT])
@require_ta
@login_required
def update_note(note_id):
    """Update an existing note based on the provided JSON body."""
    note = Note.query.get_or_404(note_id)
    data = request.get_json()
    content = data.get(NOTE_CONTENT_FIELD)

    if content:
        note.content = content
    
    note.updated_at = datetime.utcnow()
    note.updated_by = current_user.id

    db.session.commit()
    return note.to_dict()


@notes_blueprint.route(NOTES_DELETE_ROUTE, methods=[DELETE])
@require_ta
@login_required
def delete_note(note_id):
    """Delete the note identified by ID."""
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return {"message": NOTE_DELETE_SUCCESS_MESSAGE}
