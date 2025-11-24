"""
===============================================
 Home Routes (prefixed with "/home") — Templates
===============================================

GET     /home/                     → Render the home page
GET     /home/unauthorized         → Render the unauthorized access page
GET     /home/lab-equipment        → Render the lab equipment page
GET     /home/camera-gear          → Render the camera gear page
REDIRECT home.home                 → Named route for "not found" fallback
"""

from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from models import Consumable, CameraGear, LabEquipment
from constants import (
    CAMERA_GEAR_ROUTE,
    CAMERA_GEAR_TEMPLATE,
    HOME_ROUTE,
    HOME_TEMPLATE,
    HOME_BLUEPRINT_NAME,
    LAB_EQUIPMENT_ROUTE,
    LAB_EQUIPMENT_TEMPLATE,
    CONSUMABLES_ROUTE,
    CONSUMABLES_TEMPLATE,
    UNAUTHORIZED_ROUTE,
    UNAUTHORIZED_TEMPLATE
    )
from utils import require_approved


home_blueprint = Blueprint(HOME_BLUEPRINT_NAME, __name__)


@home_blueprint.route(HOME_ROUTE)
@login_required
@require_approved
def home():
    """Render the home dashboard with aggregate stats across resource types."""

    consumables = Consumable.query.all()
    camera_gear = CameraGear.query.all()
    lab_equipment = LabEquipment.query.all()

    consumables_total = sum(c.quantity or 0 for c in consumables)
    camera_gear_total = len(camera_gear)
    lab_equipment_total = len(lab_equipment)
    inventory_total = consumables_total + camera_gear_total + lab_equipment_total

    current_app.logger.debug(f"Current user: {current_user}")
    return render_template(
        HOME_TEMPLATE,
        consumables_total=consumables_total,
        camera_gear_total=camera_gear_total,
        lab_equipment_total=lab_equipment_total,
        inventory_total=inventory_total,
    )


@home_blueprint.route(LAB_EQUIPMENT_ROUTE)
@login_required
@require_approved
def lab_equipment():
    return render_template(LAB_EQUIPMENT_TEMPLATE)

@home_blueprint.route(CAMERA_GEAR_ROUTE)
@login_required
@require_approved
def camera_gear():
    return render_template(CAMERA_GEAR_TEMPLATE)

@home_blueprint.route(CONSUMABLES_ROUTE)
@login_required
@require_approved
def consumables():
    return render_template(CONSUMABLES_TEMPLATE)












