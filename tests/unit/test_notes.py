"""Unit tests for the Note model and its methods.

Tests focus on the to_dict() method and its various branches.
"""

# pylint: disable=missing-module-docstring,import-error,line-too-long,
# pylint: disable=missing-function-docstring,missing-class-docstring,unused-import
# pylint: disable=redefined-outer-name

from datetime import datetime, timezone

import pytest

from website.models import Note, CameraGear, LabEquipment, Consumable, User
from website import db
from website.constants import UserRole


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


class TestNoteToDict:
    """Test Note.to_dict() method with various scenarios."""

    def test_with_all_fields_populated(self, app_ctx, admin_user, camera_gear_item):
        """Test to_dict with all fields populated."""
        updater = User(
            first_name="Updater",
            last_name="User",
            email="updater@test.com",
            role=UserRole.TA,
        )
        db.session.add(updater)
        db.session.commit()

        note = Note(
            content="Test content",
            camera_gear_id=camera_gear_item.id,
            created_by=admin_user.id,
            updated_by=updater.id,
            created_at=datetime(2024, 1, 1, 12, 0, 0),
            updated_at=datetime(2024, 1, 2, 12, 0, 0),
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["id"] == note.id
        assert result["content"] == "Test content"
        assert result["created_by"] == admin_user.email
        assert result["updated_by"] == updater.email
        assert result["item_type"] == "camera_gear"
        assert result["item_id"] == camera_gear_item.id
        assert result["item_name"] == "Test Camera"
        assert result["created_at"] is not None
        assert result["updated_at"] is not None
        assert result["created_at"].endswith("Z")
        assert result["updated_at"].endswith("Z")

    def test_with_camera_gear(self, app_ctx, admin_user, camera_gear_item):
        """Test to_dict with camera gear attachment."""
        note = Note(
            content="Camera note",
            camera_gear_id=camera_gear_item.id,
            created_by=admin_user.id,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["item_type"] == "camera_gear"
        assert result["item_id"] == camera_gear_item.id
        assert result["item_name"] == "Test Camera"

    def test_with_lab_equipment(self, app_ctx, admin_user, lab_equipment_item):
        """Test to_dict with lab equipment attachment."""
        note = Note(
            content="Lab note",
            lab_equipment_id=lab_equipment_item.id,
            created_by=admin_user.id,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["item_type"] == "lab_equipment"
        assert result["item_id"] == lab_equipment_item.id
        assert result["item_name"] == "Test Printer"

    def test_with_consumable(self, app_ctx, admin_user, consumable_item):
        """Test to_dict with consumable attachment."""
        note = Note(
            content="Consumable note",
            consumable_id=consumable_item.id,
            created_by=admin_user.id,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["item_type"] == "consumable"
        assert result["item_id"] == consumable_item.id
        assert result["item_name"] == "Test Film"

    def test_with_no_updated_by(self, app_ctx, admin_user, camera_gear_item):
        """Test to_dict when updated_by is None."""
        note = Note(
            content="Test content",
            camera_gear_id=camera_gear_item.id,
            created_by=admin_user.id,
            updated_by=None,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["updated_by"] is None

    def test_with_created_by_but_no_user_relationship(self, app_ctx, camera_gear_item):
        """Test to_dict when created_by exists but user relationship fails."""
        note = Note(
            content="Test content",
            camera_gear_id=camera_gear_item.id,
            created_by=99999,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["created_by"] is None

    def test_with_updated_by_but_no_user_relationship(self, app_ctx, admin_user, camera_gear_item):
        """Test to_dict when updated_by exists but user relationship fails."""
        note = Note(
            content="Test content",
            camera_gear_id=camera_gear_item.id,
            created_by=admin_user.id,
            updated_by=99999,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["updated_by"] is None

    def test_with_created_at_with_tzinfo(self, app_ctx, admin_user, camera_gear_item):
        """Test to_dict with created_at that has timezone info."""
        note = Note(
            content="Test content",
            camera_gear_id=camera_gear_item.id,
            created_by=admin_user.id,
            created_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["created_at"] is not None
        assert result["created_at"].endswith("+00:00") or "Z" in result["created_at"]

    def test_with_updated_at_with_tzinfo(self, app_ctx, admin_user, camera_gear_item):
        """Test to_dict with updated_at that has timezone info."""
        note = Note(
            content="Test content",
            camera_gear_id=camera_gear_item.id,
            created_by=admin_user.id,
            updated_at=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["updated_at"] is not None

    def test_with_no_created_at(self, app_ctx, admin_user, camera_gear_item):
        """Test to_dict when created_at is None (edge case)."""
        note = Note(
            content="Test content",
            camera_gear_id=camera_gear_item.id,
            created_by=admin_user.id,
        )
        db.session.add(note)
        db.session.commit()
        result = note.to_dict()
        assert result["created_at"] is not None

    def test_with_no_updated_at(self, app_ctx, admin_user, camera_gear_item):
        """Test to_dict when updated_at is None."""
        note = Note(
            content="Test content",
            camera_gear_id=camera_gear_item.id,
            created_by=admin_user.id,
            updated_at=None,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["updated_at"] is None

    def test_with_camera_gear_relationship_fails(self, app_ctx, admin_user):
        """Test to_dict when camera_gear_id set but relationship access fails."""
        note = Note(
            content="Test content",
            camera_gear_id=99999,
            created_by=admin_user.id,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["item_type"] is None
        assert result["item_id"] is None
        assert result["item_name"] is None

    def test_with_lab_equipment_relationship_fails(self, app_ctx, admin_user):
        """Test to_dict when lab_equipment_id set but relationship access fails."""
        note = Note(
            content="Test content",
            lab_equipment_id=99999,
            created_by=admin_user.id,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["item_type"] is None

    def test_with_consumable_relationship_fails(self, app_ctx, admin_user):
        """Test to_dict when consumable_id set but relationship access fails."""
        note = Note(
            content="Test content",
            consumable_id=99999,
            created_by=admin_user.id,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["item_type"] is None

    def test_with_camera_gear_but_no_name(self, app_ctx, admin_user):
        """Test to_dict when camera_gear exists but name is None."""
        camera_gear = CameraGear(
            name="Test",
            last_updated=datetime.utcnow(),
            updated_by=admin_user.id,
        )
        db.session.add(camera_gear)
        db.session.commit()

        note = Note(
            content="Test content",
            camera_gear_id=camera_gear.id,
            created_by=admin_user.id,
        )
        db.session.add(note)
        db.session.commit()

        result = note.to_dict()
        assert result["item_name"] == "Test"

    def test_repr(self, app_ctx, admin_user, camera_gear_item):
        """Test __repr__ method returns correct string representation."""
        note = Note(
            content="Test content",
            camera_gear_id=camera_gear_item.id,
            created_by=admin_user.id,
        )
        db.session.add(note)
        db.session.commit()

        repr_str = repr(note)
        assert repr_str == f"<Note {note.id}>"
        assert "Note" in repr_str
        assert str(note.id) in repr_str