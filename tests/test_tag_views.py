"""Tests for the tags API endpoints.

These are functional tests that test the tags endpoints with various
authentication and authorization scenarios.
"""

# pylint: disable=missing-module-docstring,import-error,line-too-long,
# pylint: disable=missing-function-docstring,missing-class-docstring,unused-import
# pylint: disable=too-many-lines,redefined-outer-name

import json

import pytest

from constants import (
    API_PREFIX,
    TAG_PREFIX,
    TAG_ALL_ROUTE,
    TAG_GET_ONE_ROUTE,
    TAG_CREATE_ROUTE,
    TAG_UPDATE_ROUTE,
    TAG_DELETE_ROUTE,
    TAG_NAME,
    TAG_NAME_REQUIRED_MESSAGE,
    TAG_DELETE_SUCCESS_MESSAGE,
    MESSAGE_KEY,
    ERROR_BAD_REQUEST,
    ERROR_NOT_AUTHORIZED,
    ERROR_NOT_FOUND,
    UserRole,
)
from models import User, Tag, db


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
def sample_tag(app_ctx):
    """Create and return a sample tag."""
    tag = Tag(name="Test Tag")
    db.session.add(tag)
    db.session.commit()
    return tag


@pytest.fixture
def multiple_tags(app_ctx):
    """Create and return multiple tags."""
    tag1 = Tag(name="Tag 1")
    tag2 = Tag(name="Tag 2")
    tag3 = Tag(name="Tag 3")
    db.session.add_all([tag1, tag2, tag3])
    db.session.commit()
    return [tag1, tag2, tag3]


class TestGetAllTags:
    """Test GET /api/v1/tags/all endpoint."""

    def test_success_as_admin(self, app, app_ctx, admin_user, sample_tag):
        """Test admin can retrieve all tags."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}{TAG_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert "tags" in data
            assert len(data["tags"]) == 1
            assert data["tags"][0]["name"] == "Test Tag"

    def test_success_as_ta(self, app, app_ctx, ta_user, sample_tag):
        """Test TA can retrieve all tags."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}{TAG_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert "tags" in data

    def test_success_as_student(self, app, app_ctx, student_user, sample_tag):
        """Test student can retrieve all tags."""
        with app.test_client() as client:
            login_user_in_client(client, student_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}{TAG_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert "tags" in data

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user):
        """Test invalid role cannot retrieve tags."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}{TAG_ALL_ROUTE}")
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_unauthenticated(self, app, app_ctx):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}{TAG_ALL_ROUTE}")
            assert rv.status_code in [401, 403, 302]

    def test_returns_empty_list_when_no_tags(self, app, app_ctx, admin_user):
        """Test returns empty list when no tags exist."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}{TAG_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["tags"] == []

    def test_returns_multiple_tags(self, app, app_ctx, admin_user, multiple_tags):
        """Test returns all tags when multiple exist."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}{TAG_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert len(data["tags"]) == 3
            tag_names = [tag["name"] for tag in data["tags"]]
            assert "Tag 1" in tag_names
            assert "Tag 2" in tag_names
            assert "Tag 3" in tag_names


class TestGetTag:
    """Test GET /api/v1/tags/one/<tag_id> endpoint."""

    def test_success_with_valid_id(self, app, app_ctx, ta_user, sample_tag):
        """Test retrieving a tag by valid ID."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}/one/{sample_tag.id}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["name"] == "Test Tag"
            assert data["id"] == sample_tag.id

    def test_success_as_admin(self, app, app_ctx, admin_user, sample_tag):
        """Test admin can retrieve a tag."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}/one/{sample_tag.id}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["name"] == "Test Tag"

    def test_returns_404_for_invalid_id(self, app, app_ctx, ta_user):
        """Test returns 404 for non-existent tag."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}/one/999")
            assert rv.status_code in [ERROR_NOT_FOUND, 302]

    def test_fails_as_student(self, app, app_ctx, student_user, sample_tag):
        """Test student cannot retrieve a tag by ID."""
        with app.test_client() as client:
            login_user_in_client(client, student_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}/one/{sample_tag.id}")
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user, sample_tag):
        """Test invalid role cannot retrieve tag."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}/one/{sample_tag.id}")
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_unauthenticated(self, app, app_ctx, sample_tag):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            rv = client.get(f"{API_PREFIX}{TAG_PREFIX}/one/{sample_tag.id}")
            assert rv.status_code in [401, 403, 302]


class TestCreateTag:
    """Test POST /api/v1/tags/ endpoint."""

    def test_success_as_ta(self, app, app_ctx, ta_user):
        """Test TA can create a tag."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {TAG_NAME: "New Tag"}
            rv = client.post(
                f"{API_PREFIX}{TAG_PREFIX}{TAG_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["name"] == "New Tag"
            assert "id" in response_data

    def test_success_as_admin(self, app, app_ctx, admin_user):
        """Test admin can create a tag."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {TAG_NAME: "Admin Tag"}
            rv = client.post(
                f"{API_PREFIX}{TAG_PREFIX}{TAG_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["name"] == "Admin Tag"

    def test_fails_missing_name(self, app, app_ctx, ta_user):
        """Test fails when name is missing."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {}
            rv = client.post(
                f"{API_PREFIX}{TAG_PREFIX}{TAG_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert MESSAGE_KEY in response_data
            assert TAG_NAME_REQUIRED_MESSAGE in response_data[MESSAGE_KEY]

    def test_fails_empty_name(self, app, app_ctx, ta_user):
        """Test fails when name is empty string."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {TAG_NAME: ""}
            rv = client.post(
                f"{API_PREFIX}{TAG_PREFIX}{TAG_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert MESSAGE_KEY in response_data

    def test_fails_as_student(self, app, app_ctx, student_user):
        """Test student cannot create a tag."""
        with app.test_client() as client:
            login_user_in_client(client, student_user)
            data = {TAG_NAME: "Student Tag"}
            rv = client.post(
                f"{API_PREFIX}{TAG_PREFIX}{TAG_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user):
        """Test invalid role cannot create tag."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            data = {TAG_NAME: "Invalid Tag"}
            rv = client.post(
                f"{API_PREFIX}{TAG_PREFIX}{TAG_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_unauthenticated(self, app, app_ctx):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            data = {TAG_NAME: "Unauth Tag"}
            rv = client.post(
                f"{API_PREFIX}{TAG_PREFIX}{TAG_CREATE_ROUTE}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code in [401, 403, 302]


class TestUpdateTag:
    """Test PUT /api/v1/tags/<tag_id> endpoint."""

    def test_success_as_ta(self, app, app_ctx, ta_user, sample_tag):
        """Test TA can update a tag."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {TAG_NAME: "Updated Tag"}
            rv = client.put(
                f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["name"] == "Updated Tag"
            assert response_data["id"] == sample_tag.id

    def test_success_as_admin(self, app, app_ctx, admin_user, sample_tag):
        """Test admin can update a tag."""
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            data = {TAG_NAME: "Admin Updated"}
            rv = client.put(
                f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert response_data["name"] == "Admin Updated"

    def test_fails_missing_name(self, app, app_ctx, ta_user, sample_tag):
        """Test fails when name is missing."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {}
            rv = client.put(
                f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert MESSAGE_KEY in response_data
            assert TAG_NAME_REQUIRED_MESSAGE in response_data[MESSAGE_KEY]

    def test_fails_empty_name(self, app, app_ctx, ta_user, sample_tag):
        """Test fails when name is empty string."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {TAG_NAME: ""}
            rv = client.put(
                f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_BAD_REQUEST
            response_data = json.loads(rv.data)
            assert MESSAGE_KEY in response_data

    def test_returns_404_for_invalid_id(self, app, app_ctx, ta_user):
        """Test returns 404 for non-existent tag."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            data = {TAG_NAME: "Updated Tag"}
            rv = client.put(
                f"{API_PREFIX}{TAG_PREFIX}/999",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code in [ERROR_NOT_FOUND, 302]

    def test_fails_as_student(self, app, app_ctx, student_user, sample_tag):
        """Test student cannot update a tag."""
        with app.test_client() as client:
            login_user_in_client(client, student_user)
            data = {TAG_NAME: "Student Updated"}
            rv = client.put(
                f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user, sample_tag):
        """Test invalid role cannot update tag."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            data = {TAG_NAME: "Invalid Updated"}
            rv = client.put(
                f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_unauthenticated(self, app, app_ctx, sample_tag):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            data = {TAG_NAME: "Unauth Updated"}
            rv = client.put(
                f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}",
                data=json.dumps(data),
                content_type="application/json",
            )
            assert rv.status_code in [401, 403, 302]


class TestDeleteTag:
    """Test DELETE /api/v1/tags/<tag_id> endpoint."""

    def test_success_as_ta(self, app, app_ctx, ta_user, sample_tag):
        """Test TA can delete a tag."""
        tag_id = sample_tag.id
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.delete(f"{API_PREFIX}{TAG_PREFIX}/{tag_id}")
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert MESSAGE_KEY in response_data
            assert TAG_DELETE_SUCCESS_MESSAGE in response_data[MESSAGE_KEY]

            with app.app_context():
                deleted_tag = Tag.query.get(tag_id)
                assert deleted_tag is None

    def test_success_as_admin(self, app, app_ctx, admin_user, sample_tag):
        """Test admin can delete a tag."""
        tag_id = sample_tag.id
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.delete(f"{API_PREFIX}{TAG_PREFIX}/{tag_id}")
            assert rv.status_code == 200
            response_data = json.loads(rv.data)
            assert MESSAGE_KEY in response_data

    def test_returns_404_for_invalid_id(self, app, app_ctx, ta_user):
        """Test returns 404 for non-existent tag."""
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.delete(f"{API_PREFIX}{TAG_PREFIX}/999")
            assert rv.status_code in [ERROR_NOT_FOUND, 302]

    def test_fails_as_student(self, app, app_ctx, student_user, sample_tag):
        """Test student cannot delete a tag."""
        with app.test_client() as client:
            login_user_in_client(client, student_user)
            rv = client.delete(f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}")
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_as_invalid_role(self, app, app_ctx, invalid_user, sample_tag):
        """Test invalid role cannot delete tag."""
        with app.test_client() as client:
            login_user_in_client(client, invalid_user)
            rv = client.delete(f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}")
            assert rv.status_code == ERROR_NOT_AUTHORIZED

    def test_fails_unauthenticated(self, app, app_ctx, sample_tag):
        """Test unauthenticated request fails."""
        with app.test_client() as client:
            rv = client.delete(f"{API_PREFIX}{TAG_PREFIX}/{sample_tag.id}")
            assert rv.status_code in [401, 403, 302]