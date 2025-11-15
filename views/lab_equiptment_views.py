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

from flask import Blueprint, request
from flask_login import current_user, login_required

from constants import (
    DELETE,
    GET,
    LAB_EQUIPMENT_ALL_ROUTE,
    LAB_EQUIPMENT_CREATE_ROUTE,
    LAB_EQUIPMENT_DEFAULT_NAME,
    LAB_EQUIPMENT_DELETE_ROUTE,
    LAB_EQUIPMENT_NAME_FIELD,
    LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD,
    LAB_EQUIPMENT_TAGS_FIELD,
    LAB_EQUIPMENT_UPDATE_ROUTE,
    POST,
    PUT,
)
from models import LabEquipment, Tag, db
from utils import require_approved


lab_equipment_blueprint = Blueprint(LAB_EQUIPMENT_DEFAULT_NAME, __name__)


@lab_equipment_blueprint.route(LAB_EQUIPMENT_ALL_ROUTE, methods=[GET])
@login_required
@require_approved
def get_all_lab_equipment():
    all_equipment = LabEquipment.query.all()
    return {
        LAB_EQUIPMENT_DEFAULT_NAME: [
            equipment_item.to_dict() for equipment_item in all_equipment
        ]
    }


@lab_equipment_blueprint.route(LAB_EQUIPMENT_DEFAULT_NAME, methods=[GET])
@login_required
@require_approved
def get_lab_equipment(tag_id):
    equipment_item = LabEquipment.query.get_or_404(tag_id)
    return equipment_item.to_dict()


@lab_equipment_blueprint.route(LAB_EQUIPMENT_CREATE_ROUTE, methods=[POST])
@login_required
@require_approved
def create_lab_equipment():
    data = request.get_json()
    name = data.get(LAB_EQUIPMENT_NAME_FIELD)
    tag_names = data.get(LAB_EQUIPMENT_TAGS_FIELD)
    service_freq = data.get(LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD)

    tags = []
    if tag_names:
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
            tags.append(tag)

    new_equipment = LabEquipment(
        name=name,
        tags=tags,
        service_frequency=service_freq,
        last_updated=datetime.now(),  # Fix: Set the current datetime
        updated_by=current_user.id,  # Fix: Set the user ID instead of user object
    )

    db.session.add(new_equipment)
    db.session.commit()

    return new_equipment.to_dict()


@lab_equipment_blueprint.route(LAB_EQUIPMENT_UPDATE_ROUTE, methods=[PUT])
@login_required
@require_approved
def update_lab_equipment(lab_equipment_id):
    target_equipment = LabEquipment.query.get_or_404(lab_equipment_id)
    data = request.get_json()
    name = data.get(LAB_EQUIPMENT_NAME_FIELD)
    tag_names = data.get(LAB_EQUIPMENT_TAGS_FIELD)
    service_freq = data.get(LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD)
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

    db.session.commit()
    return {}


@lab_equipment_blueprint.route(LAB_EQUIPMENT_DELETE_ROUTE, methods=[DELETE])
@login_required
@require_approved
def delete_lab_equipment(lab_equipment_id):
    target_equipment = LabEquipment.query.get_or_404(lab_equipment_id)
    db.session.delete(target_equipment)
    db.session.commit()
    return {}
