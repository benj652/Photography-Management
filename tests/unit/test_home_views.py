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

