"""Tests for the home views dashboard and template routes.

These tests focus on the aggregate statistics shown on the home page
and the simple template-only routes for the other home subpages.
"""

# pylint: disable=import-error,wrong-import-position,redefined-outer-name,unused-argument

from datetime import datetime, timedelta, date
from unittest.mock import Mock, patch

import pytest

from website import db
from website.constants import (
    HOME_PREFIX,
    HOME_ROUTE,
    HOME_TEMPLATE,
    LAB_EQUIPMENT_ROUTE,
    LAB_EQUIPMENT_TEMPLATE,
    CAMERA_GEAR_ROUTE,
    CAMERA_GEAR_TEMPLATE,
    CONSUMABLES_ROUTE,
    CONSUMABLES_TEMPLATE,
    ERROR_NOT_AUTHORIZED,
    UserRole,
)
from website.models import Consumable, CameraGear, LabEquipment


def make_user(role=UserRole.ADMIN, is_authenticated=True):
    """Create a mock user compatible with flask-login decorators."""
    user = Mock()
    user.role = role
    user.is_authenticated = is_authenticated
    return user


def test_home_dashboard_renders_aggregate_stats(app, app_ctx):
    """Ensure the home dashboard computes and passes aggregate stats to the template."""
    today = date.today()
    now = datetime.utcnow()

    fresh_film = Consumable(
        name="Fresh Film",
        quantity=5,
        expires=today + timedelta(days=5),
        last_updated=now,
        updated_by=None,
    )
    low_paper = Consumable(
        name="Low Paper",
        quantity=0,
        expires=today + timedelta(days=10),
        last_updated=now,
        updated_by=None,
    )
    expired_ink = Consumable(
        name="Expired Ink",
        quantity=2,
        expires=today - timedelta(days=1),
        last_updated=now,
        updated_by=None,
    )

    checked_out_camera = CameraGear(
        name="Camera Checked Out",
        last_updated=now,
        updated_by=None,
        is_checked_out=True,
    )
    available_camera = CameraGear(
        name="Camera Available",
        last_updated=now,
        updated_by=None,
        is_checked_out=False,
    )

    upcoming_equipment = LabEquipment(
        name="Scanner Soon",
        last_updated=now,
        updated_by=None,
        service_frequency="weekly",
        last_serviced_on=today - timedelta(days=3),
    )
    overdue_equipment = LabEquipment(
        name="Printer Late",
        last_updated=now,
        updated_by=None,
        service_frequency="weekly",
        last_serviced_on=today - timedelta(days=10),
    )
    unscheduled_equipment = LabEquipment(
        name="Cutter Missing Date",
        last_updated=now,
        updated_by=None,
        service_frequency="monthly",
        last_serviced_on=None,
    )
    ignored_equipment = LabEquipment(
        name="No Frequency",
        last_updated=now,
        updated_by=None,
        service_frequency="custom",
        last_serviced_on=today,
    )
