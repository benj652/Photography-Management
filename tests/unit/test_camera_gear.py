# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,too-few-public-methods,too-many-instance-attributes,unused-import,unused-argument
from types import SimpleNamespace
from datetime import datetime

from website.models import CameraGear


def test_to_dict_basic():
    user = SimpleNamespace(email="up@example.com")
    checked_user = SimpleNamespace(email="checked@example.com")
    loc = SimpleNamespace(name="Cabinet")
    tag = SimpleNamespace(name="lens")

    dummy = SimpleNamespace(
        id=1,
        name="Canon 5D",
        tags=[tag],
        location=loc,
        location_id=2,
        last_updated=datetime.utcnow(),
        updated_by=11,
        updated_by_user=user,
        is_checked_out=True,
        checked_out_by=12,
        checked_out_by_user=checked_user,
        checked_out_date=datetime.utcnow(),
        return_date=None,
    )

    d = CameraGear.to_dict(dummy)
    assert d["id"] == 1
    assert d["name"] == "Canon 5D"
    assert isinstance(d["tags"], list) and "lens" in d["tags"]
    assert d["location"] == "Cabinet"
    assert d["updated_by"] == "up@example.com"
    assert d["is_checked_out"] is True
    assert d["checked_out_by"] == "checked@example.com"


def test_to_dict_handles_missing_relations():
    dummy = SimpleNamespace(
        id=2,
        name="Tripod",
        tags=[],
        location=None,
        location_id=None,
        last_updated=None,
        updated_by=None,
        updated_by_user=None,
        is_checked_out=False,
        checked_out_by=None,
        checked_out_by_user=None,
        checked_out_date=None,
        return_date=None,
    )

    d = CameraGear.to_dict(dummy)
    assert d["location"] is None
    assert d["tags"] == []
    assert d["updated_by"] is None
    assert d["is_checked_out"] is False


def test_location_name_access_raises():
    class BadLocation:
        @property
        def name(self):
            raise RuntimeError("boom")

    dummy = SimpleNamespace(
        id=3,
        name="BadLoc",
        tags=[],
        location=BadLocation(),
        location_id=None,
        last_updated=datetime.utcnow(),
        updated_by=None,
        updated_by_user=None,
        is_checked_out=False,
        checked_out_by=None,
        checked_out_by_user=None,
        checked_out_date=None,
        return_date=None,
    )

    d = CameraGear.to_dict(dummy)
    assert d["location"] is None


def test_repr_returns_expected_string():
    dummy = SimpleNamespace(name="GearRepr")
    assert CameraGear.__repr__(dummy) == "<CameraGear GearRepr>"
