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
from datetime import datetime
from flask import Blueprint, request
from flask_login import current_user
from constants import (
    DELETE,
    GET,
    LAB_EQUIPMENT_ALL_ROUTE,
    LAB_EQUIPMENT_CREATE_ROUTE,
    LAB_EQUIPMENT_DEFAULT_NAME,
    LAB_EQUIPMENT_DELETE_ROUTE,
    LAB_EQUIPMENT_GET_ONE_ROUTE,
    LAB_EQUIPMENT_NAME_FIELD,
    LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD,
    LAB_EQUIPMENT_TAGS_FIELD,
    LAB_EQUIPMENT_UPDATE_ROUTE,
    POST,
    PUT,
)
from models import LabEquipment, Tag, db
from utils import require_approved, require_ta


lab_equipment_blueprint = Blueprint(LAB_EQUIPMENT_DEFAULT_NAME, __name__)


@lab_equipment_blueprint.route(LAB_EQUIPMENT_ALL_ROUTE, methods=[GET])
@require_approved
def get_all_lab_equipment():
    """Return all lab equipment items as a list of dicts."""
    all_equipment = LabEquipment.query.all()
    return {LAB_EQUIPMENT_DEFAULT_NAME: [equipment_item.to_dict() for equipment_item in all_equipment]}


@lab_equipment_blueprint.route(LAB_EQUIPMENT_GET_ONE_ROUTE, methods=[GET])
@require_ta
def get_lab_equipment(equipment_id):
    """Return a single lab equipment item by ID."""
    equipment_item = LabEquipment.query.get_or_404(equipment_id)
    return equipment_item.to_dict()


@lab_equipment_blueprint.route(LAB_EQUIPMENT_CREATE_ROUTE, methods=[POST])
@require_ta
def create_lab_equipment():
    """Create a new lab equipment record from the provided JSON body."""

    data = request.get_json()
    name = data.get(LAB_EQUIPMENT_NAME_FIELD)
    tag_names = data.get(LAB_EQUIPMENT_TAGS_FIELD, [])
    service_freq = data.get(LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD)
    last_serviced_on = data.get("last_serviced_on")

    if not name:
        return {"error": "Name is required"}, 400

    tags = []
    if tag_names:
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)

    # Parse the date if provided
    serviced_date = None
    if last_serviced_on:
        try:
            serviced_date = datetime.strptime(last_serviced_on, "%Y-%m-%d").date()
        except ValueError:
            pass

    new_equipment = LabEquipment(
        name=name,
        tags=tags,
        service_frequency=service_freq,
        last_serviced_on=serviced_date,
        last_serviced_by=current_user.id if serviced_date else None,
        last_updated=datetime.now(),
        updated_by=current_user.id,
    )

    db.session.add(new_equipment)
    db.session.commit()

    return new_equipment.to_dict()


@lab_equipment_blueprint.route(LAB_EQUIPMENT_UPDATE_ROUTE, methods=[PUT])
@require_ta
def update_lab_equipment(equipment_id):
    """Update an existing lab equipment record with provided JSON fields."""
    target_equipment = LabEquipment.query.get_or_404(equipment_id)
    data = request.get_json()
    name = data.get(LAB_EQUIPMENT_NAME_FIELD)
    tag_names = data.get(LAB_EQUIPMENT_TAGS_FIELD)
    service_freq = data.get(LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD)
    last_serviced_on = data.get("last_serviced_on")

    if name:
        target_equipment.name = name

    if tag_names is not None:
        tags = []
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)
        target_equipment.tags = tags

    if service_freq is not None:
        target_equipment.service_frequency = service_freq

    # Handle last serviced date
    if last_serviced_on is not None:
        if last_serviced_on:  # Not empty string
            try:
                serviced_date = datetime.strptime(last_serviced_on, "%Y-%m-%d").date()
                target_equipment.last_serviced_on = serviced_date
                target_equipment.last_serviced_by = current_user.id
            except ValueError:
                pass
        else:  # Empty string, clear the date
            target_equipment.last_serviced_on = None
            target_equipment.last_serviced_by = None

    target_equipment.last_updated = datetime.now()
    target_equipment.updated_by = current_user.id

    db.session.commit()
    return target_equipment.to_dict()


@lab_equipment_blueprint.route(LAB_EQUIPMENT_DELETE_ROUTE, methods=[DELETE])
@require_ta
def delete_lab_equipment(equipment_id):
    """Delete the specified lab equipment and return a confirmation message."""
    target_equipment = LabEquipment.query.get_or_404(equipment_id)
    db.session.delete(target_equipment)
    db.session.commit()
    return {"message": "Lab equipment deleted successfully"}
