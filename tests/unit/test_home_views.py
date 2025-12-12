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

    db.session.add_all(
        [
            fresh_film,
            low_paper,
            expired_ink,
            checked_out_camera,
            available_camera,
            upcoming_equipment,
            overdue_equipment,
            unscheduled_equipment,
            ignored_equipment,
        ]
    )
    db.session.commit()

    mock_user = make_user(UserRole.ADMIN)
    with app.test_client() as client:
        with patch("flask_login.utils._get_user", return_value=mock_user):
            with patch("website.views.home_views.render_template") as mock_render:
                mock_render.return_value = "rendered"
                response = client.get(f"{HOME_PREFIX}{HOME_ROUTE}")

    assert response.status_code == 200
    mock_render.assert_called_once()
    assert mock_render.call_args.args[0] == HOME_TEMPLATE
    context = mock_render.call_args.kwargs

    assert context["consumables_total"] == 7
    assert context["camera_gear_total"] == 2
    assert context["lab_equipment_total"] == 4
    assert context["inventory_total"] == 13

    assert context["next_expiring"] is fresh_film
    assert context["days_until_expiration"] == 5
    assert context["expired_count"] == 1
    assert context["expiring_soon_count"] == 2
    assert context["out_of_stock_count"] == 1
    assert context["checked_out_count"] == 1

    next_due_date = today + timedelta(days=4)
    assert context["next_service_equipment"] is upcoming_equipment
    assert context["days_until_service"] == 4
    assert context["next_service_date"] == next_due_date
    assert context["service_overdue"] == [overdue_equipment, unscheduled_equipment]


def test_home_dashboard_handles_empty_inventory(app, app_ctx):
    """When no inventory exists, verify the template receives zeroed statistics."""
    mock_user = make_user(UserRole.TA)
    with app.test_client() as client:
        with patch("flask_login.utils._get_user", return_value=mock_user):
            with patch("website.views.home_views.render_template") as mock_render:
                mock_render.return_value = "rendered"
                response = client.get(f"{HOME_PREFIX}{HOME_ROUTE}")

    assert response.status_code == 200
    mock_render.assert_called_once()
    context = mock_render.call_args.kwargs

    assert context["consumables_total"] == 0
    assert context["camera_gear_total"] == 0
    assert context["lab_equipment_total"] == 0
    assert context["inventory_total"] == 0
    assert context["next_expiring"] is None
    assert context["days_until_expiration"] is None
    assert context["expired_count"] == 0
    assert context["expiring_soon_count"] == 0
    assert context["out_of_stock_count"] == 0
    assert context["checked_out_count"] == 0
    assert context["next_service_equipment"] is None
    assert context["days_until_service"] is None
    assert context["next_service_date"] is None
    assert context["service_overdue"] == []


def test_home_dashboard_handles_non_comparable_service_dates(app, app_ctx):
    """Guard against odd data causing the service scheduling branch to skip."""
    now = datetime.utcnow()
    equipment = LabEquipment(
        name="Weird Comparator",
        last_updated=now,
        updated_by=None,
        service_frequency="weekly",
        last_serviced_on=date.today(),
    )
    db.session.add(equipment)
    db.session.commit()

    class FakeComparable:
        def __lt__(self, other):
            return False

        def __ge__(self, other):
            return False

    class FakeDate:
        def __add__(self, delta):
            # returning a comparable object ensures the first branch is skipped
            return FakeComparable()

    with db.session.no_autoflush:
        equipment.last_serviced_on = FakeDate()
        mock_user = make_user(UserRole.ADMIN)
        with app.test_client() as client:
            with patch("flask_login.utils._get_user", return_value=mock_user):
                with patch("website.views.home_views.render_template") as mock_render:
                    mock_render.return_value = "rendered"
                    response = client.get(f"{HOME_PREFIX}{HOME_ROUTE}")

    assert response.status_code == 200
    mock_render.assert_called_once()
    context = mock_render.call_args.kwargs
    assert context["service_overdue"] == []
    assert context["next_service_equipment"] is None


def test_home_requires_approved_role(app, app_ctx):
    """Invalid roles should be rejected by the require_approved decorator."""
    mock_user = make_user(UserRole.INVALID)
    with app.test_client() as client:
        with patch("flask_login.utils._get_user", return_value=mock_user):
            response = client.get(f"{HOME_PREFIX}{HOME_ROUTE}")

    assert response.status_code == ERROR_NOT_AUTHORIZED


@pytest.mark.parametrize(
    ("route", "template"),
    [
        (LAB_EQUIPMENT_ROUTE, LAB_EQUIPMENT_TEMPLATE),
        (CAMERA_GEAR_ROUTE, CAMERA_GEAR_TEMPLATE),
        (CONSUMABLES_ROUTE, CONSUMABLES_TEMPLATE),
    ],
)

def test_home_subpages_render_templates(route, template, app, app_ctx):
    """Each secondary home route should render the corresponding template."""
    mock_user = make_user(UserRole.STUDENT)
    with app.test_client() as client:
        with patch("flask_login.utils._get_user", return_value=mock_user):
            with patch("website.views.home_views.render_template") as mock_render:
                mock_render.return_value = "rendered"
                response = client.get(f"{HOME_PREFIX}{route}")

    assert response.status_code == 200
    mock_render.assert_called_once_with(template)
