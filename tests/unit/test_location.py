"""Tests for the Location model helper methods."""

# pylint: disable=import-error,wrong-import-position

from website import db
from website.constants import LOCATION_ID, LOCATION_NAME
from website.models import Location


def test_location_to_dict_returns_expected_fields(app_ctx):
    """Ensure `to_dict` exposes the id and name fields."""
    location = Location(name="Darkroom Shelf")
    db.session.add(location)
    db.session.commit()

    data = location.to_dict()
    assert data[LOCATION_ID] == location.id
    assert data[LOCATION_NAME] == "Darkroom Shelf"


def test_location_repr_includes_name(app_ctx):
    """`__repr__` should help debugging by including the name."""
    location = Location(name="Studio A")
    db.session.add(location)
    db.session.commit()

    assert repr(location) == "<Location Studio A>"
