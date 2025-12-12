"""Tests for lab equipment API views."""

# pylint: disable=import-error,wrong-import-position,redefined-outer-name,unused-argument

from contextlib import contextmanager
from datetime import datetime, date
from unittest.mock import Mock, patch

from website import db
from website.constants import (
    API_PREFIX,
    ERROR_NOT_AUTHORIZED,
    LAB_EQUIPMENT_ALL_ROUTE,
    LAB_EQUIPMENT_CREATE_ROUTE,
    LAB_EQUIPMENT_DEFAULT_NAME,
    LAB_EQUIPMENT_DELETE_ROUTE,
    LAB_EQUIPMENT_GET_ONE_ROUTE,
    LAB_EQUIPMENT_NAME_FIELD,
    LAB_EQUIPMENT_PREFIX,
    LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD,
    LAB_EQUIPMENT_TAGS_FIELD,
    LAB_EQUIPMENT_UPDATE_ROUTE,
    UserRole,
)
from website.models import LabEquipment, Tag
from website.views import lab_equipment_views as view_module


def make_user(role=UserRole.TA, user_id=100, is_authenticated=True):
    """Construct a mock user object compatible with flask-login."""
    user = Mock()
    user.role = role
    user.id = user_id
    user.is_authenticated = is_authenticated
    return user


@contextmanager
def mock_current_user(role=UserRole.TA, user_id=100, is_authenticated=True):
    """Patch flask-login's current user lookup during a request."""
    mock_user = make_user(role=role, user_id=user_id, is_authenticated=is_authenticated)
    with patch("flask_login.utils._get_user", return_value=mock_user):
        yield mock_user


def build_url(route, equipment_id=None):
    """Return the fully qualified API URL for the given route constant."""
    path = route
    if equipment_id is not None:
        path = path.replace("<int:equipment_id>", str(equipment_id))
    return f"{API_PREFIX}{LAB_EQUIPMENT_PREFIX}{path}"


def create_equipment(name="Printer", updated_by=1, serviced_on=None, service_frequency=None):
    """Helper to create and persist a LabEquipment record for tests."""
    equipment = LabEquipment(
        name=name,
        last_updated=datetime.utcnow(),
        updated_by=updated_by,
        last_serviced_on=serviced_on,
        service_frequency=service_frequency,
    )
    db.session.add(equipment)
    db.session.commit()
    return equipment


def test_get_all_lab_equipment_as_student(app, app_ctx):
    """Approved roles like students should list equipment."""
    create_equipment(name="Printer")
    create_equipment(name="Scanner")

    with app.test_client() as client:
        with mock_current_user(UserRole.STUDENT):
            response = client.get(build_url(LAB_EQUIPMENT_ALL_ROUTE))

    assert response.status_code == 200
    data = response.get_json()
    names = [item[LAB_EQUIPMENT_NAME_FIELD] for item in data[LAB_EQUIPMENT_DEFAULT_NAME]]
    assert {"Printer", "Scanner"} <= set(names)


def test_get_all_lab_equipment_requires_authentication(app, app_ctx):
    """Unauthenticated access should be rejected."""
    with app.test_client() as client:
        with mock_current_user(UserRole.ADMIN, is_authenticated=False):
            response = client.get(build_url(LAB_EQUIPMENT_ALL_ROUTE))

    assert response.status_code == ERROR_NOT_AUTHORIZED


def test_get_lab_equipment_requires_ta_role(app, app_ctx):
    """Students cannot access the TA-only detail route."""
    equipment = create_equipment()
    with app.test_client() as client:
        with mock_current_user(UserRole.STUDENT):
            response = client.get(build_url(LAB_EQUIPMENT_GET_ONE_ROUTE, equipment.id))

    assert response.status_code == ERROR_NOT_AUTHORIZED


def test_get_lab_equipment_success_as_admin(app, app_ctx):
    equipment = create_equipment(name="Darkroom Dryer")
    with app.test_client() as client:
        with mock_current_user(UserRole.ADMIN):
            response = client.get(build_url(LAB_EQUIPMENT_GET_ONE_ROUTE, equipment.id))

    assert response.status_code == 200
    assert response.get_json()[LAB_EQUIPMENT_NAME_FIELD] == "Darkroom Dryer"


def test_create_lab_equipment_with_tags_and_service_date(app, app_ctx):
    payload = {
        LAB_EQUIPMENT_NAME_FIELD: "Chemical Hood",
        LAB_EQUIPMENT_TAGS_FIELD: ["safety", "vent"],
        LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD: "monthly",
        "last_serviced_on": "2024-05-01",
    }
    with app.test_request_context(
        build_url(LAB_EQUIPMENT_CREATE_ROUTE), method="POST", json=payload
    ):
        with mock_current_user(UserRole.TA, user_id=77):
            data = view_module.create_lab_equipment()

    assert data[LAB_EQUIPMENT_NAME_FIELD] == "Chemical Hood"
    assert set(data[LAB_EQUIPMENT_TAGS_FIELD]) == {"safety", "vent"}
    equipment = LabEquipment.query.get(data["id"])
    assert equipment.last_serviced_on == date(2024, 5, 1)
    assert equipment.last_serviced_by == 77
    # tags should be created if missing
    assert Tag.query.filter_by(name="safety").first() is not None


def test_create_lab_equipment_missing_name_returns_400(app, app_ctx):
    with app.test_request_context(
        build_url(LAB_EQUIPMENT_CREATE_ROUTE), method="POST", json={}
    ):
        with mock_current_user(UserRole.TA):
            response = view_module.create_lab_equipment()

    assert isinstance(response, tuple)
    body, status = response
    assert status == 400
    assert body["error"] == "Name is required"


def test_create_lab_equipment_invalid_date_ignored(app, app_ctx):
    payload = {
        LAB_EQUIPMENT_NAME_FIELD: "Dryer",
        "last_serviced_on": "not-a-date",
    }
    with app.test_request_context(
        build_url(LAB_EQUIPMENT_CREATE_ROUTE), method="POST", json=payload
    ):
        with mock_current_user(UserRole.TA):
            data = view_module.create_lab_equipment()

    assert data["last_serviced_on"] is None
    equipment = LabEquipment.query.get(data["id"])
    assert equipment.last_serviced_on is None
    assert equipment.last_serviced_by is None


def test_update_lab_equipment_modifies_all_fields(app, app_ctx):
    equipment = create_equipment(name="Old", service_frequency="monthly")

    with app.test_client() as client:
        with mock_current_user(UserRole.TA, user_id=88):
            response = client.put(
                build_url(LAB_EQUIPMENT_UPDATE_ROUTE, equipment.id),
                json={
                    LAB_EQUIPMENT_NAME_FIELD: "New Name",
                    LAB_EQUIPMENT_TAGS_FIELD: ["digital"],
                    LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD: "weekly",
                    "last_serviced_on": "2024-06-01",
                },
            )

    assert response.status_code == 200
    updated = LabEquipment.query.get(equipment.id)
    assert updated.name == "New Name"
    assert [t.name for t in updated.tags] == ["digital"]
    assert updated.service_frequency == "weekly"
    assert updated.last_serviced_on == date(2024, 6, 1)
    assert updated.last_serviced_by == 88


def test_update_lab_equipment_keeps_tags_when_none(app, app_ctx):
    equipment = create_equipment(name="Keep Tags")
    tag = Tag(name="existing")
    db.session.add(tag)
    db.session.commit()
    equipment.tags = [tag]
    db.session.commit()

    with app.test_client() as client:
        with mock_current_user(UserRole.TA):
            response = client.put(
                build_url(LAB_EQUIPMENT_UPDATE_ROUTE, equipment.id),
                json={
                    LAB_EQUIPMENT_NAME_FIELD: "Keep Tags",
                    LAB_EQUIPMENT_SERVICE_FREQUENCY_FIELD: "monthly",
                    # omit tags so they remain unchanged
                },
            )

    assert response.status_code == 200
    refreshed = LabEquipment.query.get(equipment.id)
    assert [t.name for t in refreshed.tags] == ["existing"]


def test_update_lab_equipment_clears_service_date(app, app_ctx):
    equipment = create_equipment(
        name="Cleaner",
        serviced_on=date(2024, 1, 1),
        service_frequency="monthly",
    )
    equipment.last_serviced_by = 10
    db.session.commit()

    with app.test_client() as client:
        with mock_current_user(UserRole.TA):
            response = client.put(
                build_url(LAB_EQUIPMENT_UPDATE_ROUTE, equipment.id),
                json={"last_serviced_on": ""},
            )

    assert response.status_code == 200
    refreshed = LabEquipment.query.get(equipment.id)
    assert refreshed.last_serviced_on is None
    assert refreshed.last_serviced_by is None


def test_update_lab_equipment_invalid_date_keeps_previous(app, app_ctx):
    equipment = create_equipment(
        name="Imager",
        serviced_on=date(2024, 3, 10),
        service_frequency="monthly",
    )
    equipment.last_serviced_by = 5
    db.session.commit()

    with app.test_client() as client:
        with mock_current_user(UserRole.TA, user_id=999):
            response = client.put(
                build_url(LAB_EQUIPMENT_UPDATE_ROUTE, equipment.id),
                json={"last_serviced_on": "bad-date"},
            )

    assert response.status_code == 200
    refreshed = LabEquipment.query.get(equipment.id)
    assert refreshed.last_serviced_on == date(2024, 3, 10)
    # last_serviced_by should remain unchanged because parse failed
    assert refreshed.last_serviced_by == 5


def test_delete_lab_equipment_removes_record(app, app_ctx):
    equipment = create_equipment(name="Old Machine")

    with app.test_client() as client:
        with mock_current_user(UserRole.TA):
            response = client.delete(build_url(LAB_EQUIPMENT_DELETE_ROUTE, equipment.id))

    assert response.status_code == 200
    assert response.get_json()["message"] == "Lab equipment deleted successfully"
    assert LabEquipment.query.get(equipment.id) is None
