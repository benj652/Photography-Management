"""Tests for the LabEquipment model helpers."""

# pylint: disable=import-error,wrong-import-position

from datetime import datetime, date
from types import SimpleNamespace

from website.models import LabEquipment


def test_to_dict_includes_relationship_fields():
    """The serialization should include tags and serviced metadata."""
    updater = SimpleNamespace(email="updater@example.com")
    serviced_by = SimpleNamespace(email="tech@example.com")
    tag = SimpleNamespace(name="printer")
    dummy = SimpleNamespace(
        id=1,
        name="Laser Printer",
        tags=[tag],
        last_updated=datetime(2024, 1, 1, 12, 0, 0),
        updated_by=2,
        updated_by_user=updater,
        last_serviced_on=date(2024, 1, 15),
        last_serviced_by=3,
        last_serviced_by_user=serviced_by,
        service_frequency="monthly",
    )

    data = LabEquipment.to_dict(dummy)
    assert data["id"] == 1
    assert data["name"] == "Laser Printer"
    assert data["tags"] == ["printer"]
    assert data["last_updated"] == "2024-01-01T12:00:00"
    assert data["updated_by"] == "updater@example.com"
    assert data["last_serviced_on"] == "2024-01-15"
    assert data["last_serviced_by"] == "tech@example.com"
    assert data["service_frequency"] == "monthly"


def test_to_dict_handles_missing_relationships():
    """Missing optional fields should yield sensible defaults."""
    dummy = SimpleNamespace(
        id=2,
        name="Scanner",
        tags=[],
        last_updated=None,
        updated_by=None,
        updated_by_user=None,
        last_serviced_on=None,
        last_serviced_by=None,
        last_serviced_by_user=None,
        service_frequency=None,
    )

    data = LabEquipment.to_dict(dummy)
    assert data["tags"] == []
    assert data["last_updated"] is None
    assert data["updated_by"] is None
    assert data["last_serviced_on"] is None
    assert data["last_serviced_by"] is None
    assert data["service_frequency"] is None


def test_to_dict_catches_relationship_errors():
    """If accessing related users raises, the serializer should still succeed."""

    class BadEquipment:
        id = 3
        name = "Broken"
        tags = []
        last_updated = datetime.utcnow()
        service_frequency = None
        last_serviced_on = None

        @property
        def updated_by(self):
            return 9

        @property
        def updated_by_user(self):
            raise RuntimeError("boom")

        @property
        def last_serviced_by(self):
            return 7

        @property
        def last_serviced_by_user(self):
            raise RuntimeError("boom")

    data = LabEquipment.to_dict(BadEquipment())
    assert data["updated_by"] is None
    assert data["last_serviced_by"] is None


def test_repr_includes_name():
    dummy = SimpleNamespace(name="Darkroom Dryer")
    assert LabEquipment.__repr__(dummy) == "<LabEquipment Darkroom Dryer>"
