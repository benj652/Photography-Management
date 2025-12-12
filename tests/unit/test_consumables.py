# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,too-few-public-methods,too-many-instance-attributes,unused-import,unused-argument
import types
from datetime import datetime, date

from types import SimpleNamespace

import pytest

from website.models import Consumable


def test_to_dict_with_location_and_updater():
    # Build a lightweight object with the attributes used by to_dict and call
    # the unbound Consumable.to_dict with that object as 'self'. This avoids
    # touching the DB while still exercising the serialization logic.
    user = SimpleNamespace(email="u@example.com")
    loc = SimpleNamespace(name="Storage")
    tag = SimpleNamespace(name="film")

    dummy = SimpleNamespace(
        id=1,
        name="Acme Film",
        quantity=5,
        tags=[tag],
        location=loc,
        location_id=10,
        expires=date(2025, 12, 31),
        last_updated=datetime.utcnow(),
        updated_by=42,
        updated_by_user=user,
    )

    d = Consumable.to_dict(dummy)
    assert d["id"] == 1
    assert d["name"] == "Acme Film"
    assert d["quantity"] == 5
    assert isinstance(d["tags"], list) and "film" in d["tags"]
    assert d["location"] == "Storage"
    assert d["expires"] == "2025-12-31"
    assert d["last_updated"] is not None
    assert d["updated_by"] == "u@example.com"


def test_to_dict_handles_missing_relations():
    dummy = SimpleNamespace(
        id=2,
        name="Paper",
        quantity=2,
        tags=[],
        location=None,
        location_id=None,
        expires=None,
        last_updated=datetime.utcnow(),
        updated_by=None,
        updated_by_user=None,
    )

    d = Consumable.to_dict(dummy)
    assert d["location"] is None
    assert d["tags"] == []
    assert d["updated_by"] is None


def test_location_name_access_raises():
    """If accessing location.name raises, location should be None in output."""
    class BadLocation:
        @property
        def name(self):
            raise RuntimeError("boom")

    dummy = SimpleNamespace(
        id=3,
        name="X",
        quantity=1,
        tags=[],
        location=BadLocation(),
        location_id=None,
        expires=None,
        last_updated=datetime.utcnow(),
        updated_by=None,
        updated_by_user=None,
    )

    d = Consumable.to_dict(dummy)
    assert d["location"] is None


def test_updated_by_without_updated_by_user_uses_id():
    dummy = SimpleNamespace(
        id=4,
        name="Y",
        quantity=2,
        tags=[],
        location=None,
        location_id=None,
        expires=None,
        last_updated=datetime.utcnow(),
        updated_by=7,
        updated_by_user=None,
    )

    d = Consumable.to_dict(dummy)
    assert d["updated_by"] == 7


def test_last_updated_and_expires_none_produce_none_fields():
    dummy = SimpleNamespace(
        id=5,
        name="Z",
        quantity=0,
        tags=[],
        location=None,
        location_id=None,
        expires=None,
        last_updated=None,
        updated_by=None,
        updated_by_user=None,
    )

    d = Consumable.to_dict(dummy)
    assert d["last_updated"] is None
    assert d["expires"] is None


def test_repr_returns_expected_string():
    dummy = SimpleNamespace(name="ReprMe")
    assert Consumable.__repr__(dummy) == "<Consumable ReprMe>"


def test_updated_by_try_block_raises_and_is_handled():
    class BadUpdatedBy:
        def __init__(self):
            self.id = 9
            self.name = "B"
            self.quantity = 1
            self.tags = []
            self.location = None
            self.location_id = None
            self.expires = None
            self.last_updated = datetime.utcnow()
            self.updated_by_user = None

        def __getattribute__(self, item):
            if item == "updated_by":
                raise RuntimeError("boom")
            return object.__getattribute__(self, item)

    dummy = BadUpdatedBy()
    d = Consumable.to_dict(dummy)
    # when reading updated_by raises, to_dict should set updated_by to None
    assert d["updated_by"] is None


def test_tags_with_none_name_included():
    """If a tag exists but its name is None, the tags list should include None."""
    tag = SimpleNamespace(name=None)
    dummy = SimpleNamespace(
        id=6,
        name="T",
        quantity=1,
        tags=[tag],
        location=None,
        location_id=None,
        expires=None,
        last_updated=datetime.utcnow(),
        updated_by=None,
        updated_by_user=None,
    )

    d = Consumable.to_dict(dummy)
    assert isinstance(d["tags"], list)
    assert d["tags"][0] is None


def test_missing_tags_attr_defaults_to_empty_list():
    """If the object has no 'tags' attribute, to_dict should return an empty tags list."""
    dummy = SimpleNamespace(
        id=7,
        name="NoTags",
        quantity=0,
        # intentionally omit 'tags'
        location=None,
        location_id=None,
        expires=None,
        last_updated=datetime.utcnow(),
        updated_by=None,
        updated_by_user=None,
    )

    # remove attribute if present to simulate missing attribute
    if hasattr(dummy, "tags"):
        delattr(dummy, "tags")

    d = Consumable.to_dict(dummy)
    assert d["tags"] == []
