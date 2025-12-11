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
from datetime import date, timedelta
from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from ..models import Consumable, CameraGear, LabEquipment
from ..constants import (
    CAMERA_GEAR_ROUTE,
    CAMERA_GEAR_TEMPLATE,
    HOME_ROUTE,
    HOME_TEMPLATE,
    HOME_BLUEPRINT_NAME,
    LAB_EQUIPMENT_ROUTE,
    LAB_EQUIPMENT_TEMPLATE,
    CONSUMABLES_ROUTE,
    CONSUMABLES_TEMPLATE,
    )
from ..utils import require_approved



home_blueprint = Blueprint(HOME_BLUEPRINT_NAME, __name__)


@home_blueprint.route(HOME_ROUTE)
@login_required
@require_approved
def home():
    """Render the home dashboard with aggregate stats across resource types."""

    consumables = Consumable.query.all()
    camera_gear = CameraGear.query.all()
    lab_equipment = LabEquipment.query.all()

    today = date.today()
    consumables_total = sum(c.quantity or 0 for c in consumables)
    camera_gear_total = len(camera_gear)
    lab_equipment_total = len(lab_equipment)
    inventory_total = consumables_total + camera_gear_total + lab_equipment_total

    upcoming_expirations = [
        c
        for c in consumables
        if c.expires is not None and c.expires >= today
    ]
    next_expiring = min(upcoming_expirations, key=lambda c: c.expires, default=None)
    days_until_expiration = (
        (next_expiring.expires - today).days if next_expiring else None
    )
    expired_items = [
        c for c in consumables if c.expires is not None and c.expires < today
    ]
    expiring_soon_count = sum(
        1
        for c in upcoming_expirations
        if (c.expires - today).days <= 14
    )
    out_of_stock_count = sum(1 for c in consumables if (c.quantity or 0) <= 0)
    checked_out_count = sum(1 for g in camera_gear if g.is_checked_out)
    frequency_to_days = {
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90,
        "yearly": 365,
    }
    upcoming_service = []
    service_overdue = []
    for equipment in lab_equipment:
        freq = (equipment.service_frequency or "").lower()
        interval_days = frequency_to_days.get(freq)
        if not interval_days:
            continue
        if equipment.last_serviced_on:
            next_due = equipment.last_serviced_on + timedelta(days=interval_days)
        else:
            next_due = None

        if next_due is None or next_due < today:
            service_overdue.append(equipment)
            continue

        if next_due >= today:
            upcoming_service.append((next_due, equipment))
    next_service_equipment = None
    days_until_service = None
    next_service_date = None
    if upcoming_service:
        next_due, equipment = min(upcoming_service, key=lambda item: item[0])
        next_service_equipment = equipment
        days_until_service = (next_due - today).days
        next_service_date = next_due

    current_app.logger.debug(f"Current user: {current_user}")
    return render_template(
        HOME_TEMPLATE,
        consumables_total=consumables_total,
        camera_gear_total=camera_gear_total,
        lab_equipment_total=lab_equipment_total,
        inventory_total=inventory_total,
        next_expiring=next_expiring,
        days_until_expiration=days_until_expiration,
        expired_count=len(expired_items),
        expiring_soon_count=expiring_soon_count,
        out_of_stock_count=out_of_stock_count,
        checked_out_count=checked_out_count,
        next_service_equipment=next_service_equipment,
        days_until_service=days_until_service,
        next_service_date=next_service_date,
        service_overdue=service_overdue,
    )


@home_blueprint.route(LAB_EQUIPMENT_ROUTE)
@login_required
@require_approved
def lab_equipment():
    """Render the lab equipment page template."""
    return render_template(LAB_EQUIPMENT_TEMPLATE)

@home_blueprint.route(CAMERA_GEAR_ROUTE)
@login_required
@require_approved
def camera_gear():
    """Render the camera gear page template."""
    return render_template(CAMERA_GEAR_TEMPLATE)

@home_blueprint.route(CONSUMABLES_ROUTE)
@login_required
@require_approved
def consumables():
    """Render the consumables page template."""
    return render_template(CONSUMABLES_TEMPLATE)
