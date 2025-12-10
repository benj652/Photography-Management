"""Tests for the notes API endpoints.

These are functional tests that test the notes endpoints with various
authentication and authorization scenarios.
"""

# pylint: disable=missing-module-docstring,import-error,line-too-long,
# pylint: disable=missing-function-docstring,missing-class-docstring,unused-import
# pylint: disable=too-many-lines,redefined-outer-name

import json
from datetime import datetime

import pytest

from website.constants import (
    API_PREFIX,
    NOTES_PREFIX,
    NOTES_ALL_ROUTE,
    NOTES_GET_ONE_ROUTE,
    NOTES_BY_ITEM_ROUTE,
    NOTES_CREATE_ROUTE,
    NOTES_UPDATE_ROUTE,
    NOTES_DELETE_ROUTE,
    NOTE_CONTENT_FIELD,
    NOTE_ITEM_TYPE_FIELD,
    NOTE_ITEM_ID_FIELD,
    NOTE_CONTENT_REQUIRED_MESSAGE,
    NOTE_ITEM_TYPE_REQUIRED_MESSAGE,
    NOTE_ITEM_ID_REQUIRED_MESSAGE,
    NOTE_DELETE_SUCCESS_MESSAGE,
    ERROR_BAD_REQUEST,
    ERROR_NOT_AUTHORIZED,
    ERROR_NOT_FOUND,
    UserRole,
)
from website.models import User, Note, CameraGear, LabEquipment, Consumable
from website import db


def login_user_in_client(client, user):
    """Helper to log in a user in a test client."""
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True


@pytest.fixture
def admin_user(app_ctx):
    """Create and return an admin user."""
    user = User(
        first_name="Admin",
        last_name="User",
        email="admin@test.com",
        role=UserRole.ADMIN,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def ta_user(app_ctx):
    """Create and return a TA user."""
    user = User(
        first_name="TA",
        last_name="User",
        email="ta@test.com",
        role=UserRole.TA,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def student_user(app_ctx):
    """Create and return a student user."""
    user = User(
        first_name="Student",
        last_name="User",
        email="student@test.com",
        role=UserRole.STUDENT,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def invalid_user(app_ctx):
    """Create and return an invalid user."""
    user = User(
        first_name="Invalid",
        last_name="User",
        email="invalid@test.com",
        role=UserRole.INVALID,
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def camera_gear_item(app_ctx, admin_user):
    """Create and return a camera gear item."""
    item = CameraGear(
        name="Test Camera",
        last_updated=datetime.utcnow(),
        updated_by=admin_user.id,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture
def lab_equipment_item(app_ctx, admin_user):
    """Create and return a lab equipment item."""
    item = LabEquipment(
        name="Test Printer",
        last_updated=datetime.utcnow(),
        updated_by=admin_user.id,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture
def consumable_item(app_ctx, admin_user):
    """Create and return a consumable item."""
    item = Consumable(
        name="Test Film",
        quantity=10,
        last_updated=datetime.utcnow(),
        updated_by=admin_user.id,
    )
    db.session.add(item)
    db.session.commit()
    return item


@pytest.fixture
def note_for_camera_gear(app_ctx, camera_gear_item, admin_user):
    """Create and return a note attached to camera gear."""
    note = Note(
        content="Test note for camera gear",
        camera_gear_id=camera_gear_item.id,
        created_by=admin_user.id,
    )
    db.session.add(note)
    db.session.commit()
    return note


@pytest.fixture
def note_for_lab_equipment(app_ctx, lab_equipment_item, admin_user):
    """Create and return a note attached to lab equipment."""
    note = Note(
        content="Test note for lab equipment",
        lab_equipment_id=lab_equipment_item.id,
        created_by=admin_user.id,
    )
    db.session.add(note)
    db.session.commit()
    return note


@pytest.fixture
def note_for_consumable(app_ctx, consumable_item, admin_user):
    """Create and return a note attached to consumable."""
    note = Note(
        content="Test note for consumable",
        consumable_id=consumable_item.id,
        created_by=admin_user.id,
    )
    db.session.add(note)
    db.session.commit()
    return note


class TestGetAllNotes:
    """Test GET /api/v1/notes/all endpoint."""

    def test_success_as_admin(self, app, app_ctx, admin_user, note_for_camera_gear):
        """Test admin can retrieve all notes."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert "notes" in data
            assert len(data["notes"]) == 1
            assert data["notes"][0]["content"] == "Test note for camera gear"

    def test_success_as_ta(self, app, app_ctx, ta_user, note_for_camera_gear):
        """Test TA can retrieve all notes."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert "notes" in data

    def test_success_as_student(self, app, app_ctx, student_user, note_for_camera_gear):
        """Test student can retrieve all notes."""
        with app.test_client() as client:
            login_user_in_client(client, student_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert "notes" in data

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user):
        """Test invalid role cannot retrieve notes."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_ALL_ROUTE}")
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_unauthenticated(self, app, app_ctx):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_ALL_ROUTE}")
            assert rv.status_code in [401, 302]

    def test_returns_empty_list_when_no_notes(self, app, app_ctx, admin_user):
        """Test returns empty list when no notes exist."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["notes"] == []


class TestGetNote:
    """Test GET /api/v1/notes/one/<note_id> endpoint."""

    def test_success_with_valid_id(self, app, app_ctx, admin_user, note_for_camera_gear):
        """Test retrieving a note by valid ID."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_GET_ONE_ROUTE}".replace("<int:note_id>", str(note_for_camera_gear.id)))
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["content"] == "Test note for camera gear"
            assert data["id"] == note_for_camera_gear.id

    def test_returns_404_for_invalid_id(self, app, app_ctx, admin_user):
        """Test returns 404 for non-existent note."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}/one/999")
            assert rv.status_code in [ERROR_NOT_FOUND, 302]

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user, note_for_camera_gear):
        """Test invalid role cannot retrieve note."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_GET_ONE_ROUTE}".replace("<int:note_id>", str(note_for_camera_gear.id)))
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_unauthenticated(self, app, app_ctx, note_for_camera_gear):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}/one/{note_for_camera_gear.id}")
            assert rv.status_code in [401, 403, 302]


class TestGetNoteByItem:
    """Test GET /api/v1/notes/by-item/<item_type>/<item_id> endpoint."""

    def test_success_camera_gear_with_note(self, app, app_ctx, admin_user, note_for_camera_gear, camera_gear_item):
        """Test retrieving note for camera gear that has a note."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_BY_ITEM_ROUTE}".replace("<item_type>", "camera_gear").replace("<int:item_id>", str(camera_gear_item.id)))
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["content"] == "Test note for camera gear"

    def test_success_camera_gear_without_note(self, app, app_ctx, admin_user, camera_gear_item):
        """Test retrieving note for camera gear that has no note."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_BY_ITEM_ROUTE}".replace("<item_type>", "camera_gear").replace("<int:item_id>", str(camera_gear_item.id)))
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data == {}

    def test_success_lab_equipment_with_note(self, app, app_ctx, admin_user, note_for_lab_equipment, lab_equipment_item):
        """Test retrieving note for lab equipment that has a note."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_BY_ITEM_ROUTE}".replace("<item_type>", "lab_equipment").replace("<int:item_id>", str(lab_equipment_item.id)))
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["content"] == "Test note for lab equipment"

    def test_success_lab_equipment_without_note(self, app, app_ctx, admin_user, lab_equipment_item):
        """Test retrieving note for lab equipment that has no note."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_BY_ITEM_ROUTE}".replace("<item_type>", "lab_equipment").replace("<int:item_id>", str(lab_equipment_item.id)))
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data == {}

    def test_success_consumable_with_note(self, app, app_ctx, admin_user, note_for_consumable, consumable_item):
        """Test retrieving note for consumable that has a note."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_BY_ITEM_ROUTE}".replace("<item_type>", "consumable").replace("<int:item_id>", str(consumable_item.id)))
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["content"] == "Test note for consumable"

    def test_success_consumable_without_note(self, app, app_ctx, admin_user, consumable_item):
        """Test retrieving note for consumable that has no note."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_BY_ITEM_ROUTE}".replace("<item_type>", "consumable").replace("<int:item_id>", str(consumable_item.id)))
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data == {}

    def test_returns_400_for_invalid_item_type(self, app, app_ctx, admin_user, camera_gear_item):
        """Test returns 400 for invalid item type."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_BY_ITEM_ROUTE}".replace("<item_type>", "invalid_type").replace("<int:item_id>", str(camera_gear_item.id)))
            assert rv.status_code == ERROR_BAD_REQUEST
            data = json.loads(rv.data)
            assert "error" in data
            assert "Invalid item type" in data["error"]

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user, camera_gear_item):
        """Test invalid role cannot retrieve note by item."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_BY_ITEM_ROUTE}".replace("<item_type>", "camera_gear").replace("<int:item_id>", str(camera_gear_item.id)))
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_unauthenticated(self, app, app_ctx, camera_gear_item):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            rv = client.get(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_BY_ITEM_ROUTE}".replace("<item_type>", "camera_gear").replace("<int:item_id>", "1"))
            assert rv.status_code in [401, 302]


class TestCreateNote:
    """Test POST /api/v1/notes/ endpoint."""

    def test_success_camera_gear(self, app, app_ctx, admin_user, camera_gear_item):
        """Test creating note for camera gear."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "New note content",
                NOTE_ITEM_TYPE_FIELD: "camera_gear",
                NOTE_ITEM_ID_FIELD: camera_gear_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["content"] == "New note content"
            assert response_data["item_type"] == "camera_gear"
            assert response_data["item_id"] == camera_gear_item.id
            assert response_data["created_by"] == admin_user.email

    def test_success_lab_equipment(self, app, app_ctx, admin_user, lab_equipment_item):
        """Test creating note for lab equipment."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "New lab note",
                NOTE_ITEM_TYPE_FIELD: "lab_equipment",
                NOTE_ITEM_ID_FIELD: lab_equipment_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["content"] == "New lab note"
            assert response_data["item_type"] == "lab_equipment"

    def test_success_consumable(self, app, app_ctx, admin_user, consumable_item):
        """Test creating note for consumable."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "New consumable note",
                NOTE_ITEM_TYPE_FIELD: "consumable",
                NOTE_ITEM_ID_FIELD: consumable_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["content"] == "New consumable note"
            assert response_data["item_type"] == "consumable"

    def test_fails_missing_content(self, app, app_ctx, admin_user, camera_gear_item):
        """Test fails when content is missing."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_ITEM_TYPE_FIELD: "camera_gear",
                NOTE_ITEM_ID_FIELD: camera_gear_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data
            assert NOTE_CONTENT_REQUIRED_MESSAGE in response_data["error"]

    def test_fails_missing_item_type(self, app, app_ctx, admin_user, camera_gear_item):
        """Test fails when item_type is missing."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Test content",
                NOTE_ITEM_ID_FIELD: camera_gear_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data
            assert NOTE_ITEM_TYPE_REQUIRED_MESSAGE in response_data["error"]

    def test_fails_missing_item_id(self, app, app_ctx, admin_user):
        """Test fails when item_id is missing."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Test content",
                NOTE_ITEM_TYPE_FIELD: "camera_gear",
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data
            assert NOTE_ITEM_ID_REQUIRED_MESSAGE in response_data["error"]

    def test_fails_item_id_none(self, app, app_ctx, admin_user):
        """Test fails when item_id is None."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Test content",
                NOTE_ITEM_TYPE_FIELD: "camera_gear",
                NOTE_ITEM_ID_FIELD: None,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data

    def test_fails_invalid_item_type(self, app, app_ctx, admin_user, camera_gear_item):
        """Test fails with invalid item type."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Test content",
                NOTE_ITEM_TYPE_FIELD: "invalid_type",
                NOTE_ITEM_ID_FIELD: camera_gear_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data
            assert "Invalid item type" in response_data["error"]

    def test_fails_camera_gear_not_found(self, app, app_ctx, admin_user):
        """Test fails when camera gear item doesn't exist."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Test content",
                NOTE_ITEM_TYPE_FIELD: "camera_gear",
                NOTE_ITEM_ID_FIELD: 999,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data
            assert "not found" in response_data["error"].lower()

    def test_fails_lab_equipment_not_found(self, app, app_ctx, admin_user):
        """Test fails when lab equipment item doesn't exist."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Test content",
                NOTE_ITEM_TYPE_FIELD: "lab_equipment",
                NOTE_ITEM_ID_FIELD: 999,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data

    def test_fails_consumable_not_found(self, app, app_ctx, admin_user):
        """Test fails when consumable item doesn't exist."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Test content",
                NOTE_ITEM_TYPE_FIELD: "consumable",
                NOTE_ITEM_ID_FIELD: 999,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data

    def test_fails_camera_gear_note_already_exists(self, app, app_ctx, admin_user, note_for_camera_gear, camera_gear_item):
        """Test fails when note already exists for camera gear."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Duplicate note",
                NOTE_ITEM_TYPE_FIELD: "camera_gear",
                NOTE_ITEM_ID_FIELD: camera_gear_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data
            assert "already exists" in response_data["error"].lower()

    def test_fails_lab_equipment_note_already_exists(self, app, app_ctx, admin_user, note_for_lab_equipment, lab_equipment_item):
        """Test fails when note already exists for lab equipment."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Duplicate note",
                NOTE_ITEM_TYPE_FIELD: "lab_equipment",
                NOTE_ITEM_ID_FIELD: lab_equipment_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data

    def test_fails_consumable_note_already_exists(self, app, app_ctx, admin_user, note_for_consumable, consumable_item):
        """Test fails when note already exists for consumable."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Duplicate note",
                NOTE_ITEM_TYPE_FIELD: "consumable",
                NOTE_ITEM_ID_FIELD: consumable_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert "error" in response_data

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user, camera_gear_item):
        """Test invalid role cannot create note."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            data = {
                NOTE_CONTENT_FIELD: "Test content",
                NOTE_ITEM_TYPE_FIELD: "camera_gear",
                NOTE_ITEM_ID_FIELD: camera_gear_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_unauthenticated(self, app, app_ctx, camera_gear_item):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            data = {
                NOTE_CONTENT_FIELD: "Test content",
                NOTE_ITEM_TYPE_FIELD: "camera_gear",
                NOTE_ITEM_ID_FIELD: camera_gear_item.id,
            }
            rv = client.post(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code in [401, 403, 302]


class TestUpdateNote:
    """Test PUT /api/v1/notes/<note_id> endpoint."""

    def test_success_with_content(self, app, app_ctx, ta_user, note_for_camera_gear):
        """Test updating note content."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {
                NOTE_CONTENT_FIELD: "Updated content",
            }
            rv = client.put(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_UPDATE_ROUTE}".replace("<int:note_id>", str(note_for_camera_gear.id)),
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["content"] == "Updated content"
            assert response_data["updated_by"] == ta_user.email
            assert response_data["updated_at"] is not None

    def test_success_without_content(self, app, app_ctx, ta_user, note_for_camera_gear):
        """Test updating note without providing content."""
        original_content = note_for_camera_gear.content
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {}
            rv = client.put(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_UPDATE_ROUTE}".replace("<int:note_id>", str(note_for_camera_gear.id)),
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["content"] == original_content
            assert response_data["updated_at"] is not None

    def test_success_with_empty_content(self, app, app_ctx, ta_user, note_for_camera_gear):
        """Test updating note with empty content."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {
                NOTE_CONTENT_FIELD: "",
            }
            rv = client.put(
                f"{API_PREFIX}{NOTES_PREFIX}/{note_for_camera_gear.id}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["content"] == ""

    def test_returns_404_for_invalid_id(self, app, app_ctx, ta_user):
        """Test returns 404 for non-existent note."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {
                NOTE_CONTENT_FIELD: "Updated content",
            }
            rv = client.put(
                f"{API_PREFIX}{NOTES_PREFIX}/999",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code in [ERROR_NOT_FOUND, 302]

    def test_fails_as_student(self, app, app_ctx, student_user, note_for_camera_gear):
        """Test student cannot update note."""
        with app.test_client() as client:
            login_user_in_client(client, student_user)
            data = {
                NOTE_CONTENT_FIELD: "Updated content",
            }
            rv = client.put(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_UPDATE_ROUTE}".replace("<int:note_id>", str(note_for_camera_gear.id)),
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user, note_for_camera_gear):
        """Test invalid role cannot update note."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            data = {
                NOTE_CONTENT_FIELD: "Updated content",
            }
            rv = client.put(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_UPDATE_ROUTE}".replace("<int:note_id>", str(note_for_camera_gear.id)),
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_success_as_admin(self, app, app_ctx, admin_user, note_for_camera_gear):
        """Test admin can update note."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {
                NOTE_CONTENT_FIELD: "Admin updated content",
            }
            rv = client.put(
                f"{API_PREFIX}{NOTES_PREFIX}{NOTES_UPDATE_ROUTE}".replace("<int:note_id>", str(note_for_camera_gear.id)),
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200

    def test_fails_unauthenticated(self, app, app_ctx, note_for_camera_gear):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            data = {
                NOTE_CONTENT_FIELD: "Updated content",
            }
            rv = client.put(
                f"{API_PREFIX}{NOTES_PREFIX}/{note_for_camera_gear.id}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code in [401, 403, 302]


class TestDeleteNote:
    """Test DELETE /api/v1/notes/<note_id> endpoint."""

    def test_success(self, app, app_ctx, ta_user, note_for_camera_gear):
        """Test deleting a note."""
        note_id = note_for_camera_gear.id
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.delete(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_DELETE_ROUTE}".replace("<int:note_id>", str(note_id)))
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert "message" in response_data
            assert NOTE_DELETE_SUCCESS_MESSAGE in response_data["message"]

            with app.app_context():
                deleted_note = Note.query.get(note_id)
                assert deleted_note is None

    def test_returns_404_for_invalid_id(self, app, app_ctx, ta_user):
        """Test returns 404 for non-existent note."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.delete(f"{API_PREFIX}{NOTES_PREFIX}/999")
            assert rv.status_code in [ERROR_NOT_FOUND, 302]

    def test_fails_as_student(self, app, app_ctx, student_user, note_for_camera_gear):
        """Test student cannot delete note."""
        with app.test_client() as client:
            login_user_in_client(client, student_user)
            rv = client.delete(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_DELETE_ROUTE}".replace("<int:note_id>", str(note_for_camera_gear.id)))
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user, note_for_camera_gear):
        """Test invalid role cannot delete note."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            rv = client.delete(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_DELETE_ROUTE}".replace("<int:note_id>", str(note_for_camera_gear.id)))
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_success_as_admin(self, app, app_ctx, admin_user, note_for_camera_gear):
        """Test admin can delete note."""
        note_id = note_for_camera_gear.id
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.delete(f"{API_PREFIX}{NOTES_PREFIX}{NOTES_DELETE_ROUTE}".replace("<int:note_id>", str(note_id)))
            assert rv.status_code == 200

    def test_fails_unauthenticated(self, app, app_ctx, note_for_camera_gear):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            rv = client.delete(f"{API_PREFIX}{NOTES_PREFIX}/{note_for_camera_gear.id}")
            assert rv.status_code in [401, 403, 302]