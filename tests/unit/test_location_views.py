"""Tests for the location API views."""

# pylint: disable=import-error,wrong-import-position,redefined-outer-name,unused-argument

from contextlib import contextmanager
from unittest.mock import Mock, patch

from website import db
from website.constants import (
    API_PREFIX,
    LOCATION_PREFIX,
    LOCATION_ALL_ROUTE,
    LOCATION_GET_ONE_ROUTE,
    LOCATION_CREATE_ROUTE,
    LOCATION_UPDATE_ROUTE,
    LOCATION_DELETE_ROUTE,
    LOCATION_DEFAULT_NAME,
    LOCATION_NAME,
    LOCATION_NAME_NEEDED_MESSAGE,
    LOCATION_DELETE_SUCCESS_MESSAGE,
    MESSAGE_KEY,
    ERROR_BAD_REQUEST,
    ERROR_NOT_AUTHORIZED,
    UserRole,
)
from website.models import Location
from website.views import location_views as view_module


def make_user(role, is_authenticated=True):
    """Create a mock flask-login user for decorator checks."""
    user = Mock()
    user.role = role
    user.is_authenticated = is_authenticated
    return user


@contextmanager
def mock_current_user(role, is_authenticated=True):
    """Patch flask-login's current user proxy for the duration of a request."""
    mock_user = make_user(role, is_authenticated=is_authenticated)
    with patch("flask_login.utils._get_user", return_value=mock_user):
        yield


def build_url(route, location_id=None):
    """Return a fully-qualified API URL for the given route constant."""
    path = route
    if location_id is not None:
        path = path.replace("<int:location_id>", str(location_id))
    return f"{API_PREFIX}{LOCATION_PREFIX}{path}"


def test_get_locations_returns_all_for_student(app, app_ctx):
    """Approved roles (including students) can list all locations."""
    loc1 = Location(name="Studio A")
    loc2 = Location(name="Darkroom Shelf")
    db.session.add_all([loc1, loc2])
    db.session.commit()

    with app.test_client() as client:
        with mock_current_user(UserRole.STUDENT):
            response = client.get(build_url(LOCATION_ALL_ROUTE))

    assert response.status_code == 200
    data = response.get_json()
    assert len(data[LOCATION_DEFAULT_NAME]) == 2
    names = [entry[LOCATION_NAME] for entry in data[LOCATION_DEFAULT_NAME]]
    assert "Studio A" in names and "Darkroom Shelf" in names


def test_get_locations_requires_authentication(app, app_ctx):
    """Unauthenticated users should be rejected by require_approved."""
    with app.test_client() as client:
        with mock_current_user(UserRole.ADMIN, is_authenticated=False):
            response = client.get(build_url(LOCATION_ALL_ROUTE))

    assert response.status_code == ERROR_NOT_AUTHORIZED


def test_get_location_requires_ta_role(app, app_ctx):
    """Students lack permission to hit the TA-only detail route."""
    location = Location(name="Print Lab")
    db.session.add(location)
    db.session.commit()

    with app.test_client() as client:
        with mock_current_user(UserRole.STUDENT):
            response = client.get(build_url(LOCATION_GET_ONE_ROUTE, location.id))

    assert response.status_code == ERROR_NOT_AUTHORIZED


def test_get_location_success_as_admin(app, app_ctx):
    """Admins (and TAs) can retrieve a single location."""
    location = Location(name="Equipment Cage")
    db.session.add(location)
    db.session.commit()

    with app.test_client() as client:
        with mock_current_user(UserRole.ADMIN):
            response = client.get(build_url(LOCATION_GET_ONE_ROUTE, location.id))

    assert response.status_code == 200
    assert response.get_json()[LOCATION_NAME] == "Equipment Cage"


def test_create_location_success(app, app_ctx):
    """TA users can create new locations."""
    with app.test_client() as client:
        with mock_current_user(UserRole.TA):
            response = client.post(
                build_url(LOCATION_CREATE_ROUTE),
                json={LOCATION_NAME: "Photo Studio"},
            )

    assert response.status_code == 200
    data = response.get_json()
    assert data[LOCATION_NAME] == "Photo Studio"
    assert Location.query.filter_by(name="Photo Studio").count() == 1


def test_create_location_requires_name(app, app_ctx):
    """Missing `name` should yield a 400 with the shared error message."""
    with app.test_client() as client:
        with mock_current_user(UserRole.TA):
            response = client.post(build_url(LOCATION_CREATE_ROUTE), json={})

    assert response.status_code == ERROR_BAD_REQUEST
    assert response.get_json()[MESSAGE_KEY] == LOCATION_NAME_NEEDED_MESSAGE


def test_update_location_changes_name(app, app_ctx):
    """PUT should rename an existing location when provided a new name."""
    location = Location(name="Old Name")
    db.session.add(location)
    db.session.commit()

    with app.test_request_context(
        build_url(LOCATION_UPDATE_ROUTE, location.id),
        method="PUT",
        json={LOCATION_NAME: "New Name"},
    ):
        with mock_current_user(UserRole.TA):
            response = view_module.update_location(location_id=location.id)

    assert response[LOCATION_NAME] == "New Name"
    assert Location.query.get(location.id).name == "New Name"


def test_update_location_requires_name(app, app_ctx):
    """Update should validate inputs just like create."""
    location = Location(name="Still Old")
    db.session.add(location)
    db.session.commit()

    with app.test_request_context(
        build_url(LOCATION_UPDATE_ROUTE, location.id),
        method="PUT",
        json={},
    ):
        with mock_current_user(UserRole.TA):
            response = view_module.update_location(location_id=location.id)

    assert isinstance(response, tuple)
    assert response[1] == ERROR_BAD_REQUEST
    assert response[0][MESSAGE_KEY] == LOCATION_NAME_NEEDED_MESSAGE


def test_delete_location_removes_record(app, app_ctx):
    """Deleting returns the success message and removes the row."""
    location = Location(name="To Delete")
    db.session.add(location)
    db.session.commit()

    with app.test_client() as client:
        with mock_current_user(UserRole.TA):
            response = client.delete(build_url(LOCATION_DELETE_ROUTE, location.id))

    assert response.status_code == 200
    assert response.get_json()[MESSAGE_KEY] == LOCATION_DELETE_SUCCESS_MESSAGE
    assert Location.query.get(location.id) is None
