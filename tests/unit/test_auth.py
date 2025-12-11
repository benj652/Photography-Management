"""Tests for auth_views.py functionality.

This module tests OAuth authentication flows, user management,
and authentication-related routes with comprehensive branch coverage.
"""

# pylint: disable=import-error,wrong-import-position,redefined-outer-name,unused-argument
import os
from unittest.mock import Mock, patch, MagicMock
import pytest
from flask import url_for, session
from flask_login import current_user

from website.views.auth_views import (
    init_oauth,
    create_new_user,
    get_user,
    auth_blueprint,
    google,
)
from website.constants import (
    UserRole,
    AUTH_PREFIX,
    HOME_PREFIX,
    LOGIN_TEMPLATE,
    USER_KEY,
    GOOGLE_USER_EMAIL,
    GOOGLE_USER_GIVEN_NAME,
    GOOGLE_USER_FAMILY_NAME,
    GOOGLE_USER_PICTURE,
    DEFAULT_ADMIN_EMAIL,
)
from website.models import User


class TestInitOauth:
    """Test OAuth initialization functionality."""

    def test_init_oauth_registers_google_provider(self, app, patcher):
        """Test that init_oauth properly registers Google OAuth provider."""
        # Mock OAuth and google registration
        mock_oauth = Mock()
        mock_google = Mock()
        mock_oauth.register.return_value = mock_google

        patcher(
            os,
            "getenv",
            lambda key, default=None: {
                "GOOGLE_CLIENT_ID": "test_client_id",
                "GOOGLE_CLIENT_SECRET": "test_client_secret",
            }.get(key, default),
        )

        with patch("website.views.auth_views.oauth", mock_oauth):
            init_oauth(app)

        mock_oauth.init_app.assert_called_once_with(app)
        mock_oauth.register.assert_called_once()


class TestAuthRoutes:
    """Test authentication route handlers."""

    def test_login_route_redirects_to_google(self, app, app_ctx, patcher):
        """Test that /auth/login redirects to Google OAuth."""
        mock_google = Mock()
        mock_google.authorize_redirect.return_value = "redirect_response"

        patcher(os, "getenv", lambda key, default=None: "test_value")

        with app.test_client() as client:
            with patch("website.views.auth_views.google", mock_google):
                response = client.get("/auth/login")

        mock_google.authorize_redirect.assert_called_once()

    def test_login_page_renders_template(self, app, app_ctx):
        """Test that /auth/ renders the login template."""
        with app.test_client() as client:
            response = client.get("/auth/")

        assert response.status_code == 200
        # Template rendering is mocked in test environment, so we check the route works

    @patch("website.views.auth_views.google")
    @patch("website.views.auth_views.get_user")
    @patch("website.views.auth_views.create_new_user")
    @patch("website.views.auth_views.login_user")
    def test_authorize_with_new_user(
        self,
        mock_login_user,
        mock_create_user,
        mock_get_user,
        mock_google,
        app,
        app_ctx,
    ):
        """Test OAuth authorization flow with a new user."""
        # Setup mocks
        mock_token = {"access_token": "test_token"}
        mock_google_user_data = {
            GOOGLE_USER_EMAIL: "newuser@example.com",
            GOOGLE_USER_GIVEN_NAME: "New",
            GOOGLE_USER_FAMILY_NAME: "User",
            GOOGLE_USER_PICTURE: "http://example.com/pic.jpg",
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_google_user_data

        mock_google.authorize_access_token.return_value = mock_token
        mock_google.get.return_value = mock_response
        mock_get_user.return_value = None  # User doesn't exist

        mock_new_user = Mock()
        mock_new_user.id = 123
        mock_create_user.return_value = mock_new_user

        with app.test_client() as client:
            with client.session_transaction() as sess:
                # Simulate OAuth callback
                response = client.get("/auth/authorize")

        # Verify the flow
        mock_google.authorize_access_token.assert_called_once()
        mock_get_user.assert_called_once_with("newuser@example.com")
        mock_create_user.assert_called_once_with(mock_google_user_data)
        mock_login_user.assert_called_once_with(mock_new_user)

        assert response.status_code == 302  # Redirect after login

    @patch("website.views.auth_views.google")
    @patch("website.views.auth_views.get_user")
    @patch("website.views.auth_views.login_user")
    def test_authorize_with_existing_user(
        self, mock_login_user, mock_get_user, mock_google, app, app_ctx
    ):
        """Test OAuth authorization flow with an existing user."""
        # Setup mocks
        mock_token = {"access_token": "test_token"}
        mock_google_user_data = {
            GOOGLE_USER_EMAIL: "existing@example.com",
            GOOGLE_USER_GIVEN_NAME: "Existing",
            GOOGLE_USER_FAMILY_NAME: "User",
            GOOGLE_USER_PICTURE: "http://example.com/pic.jpg",
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_google_user_data

        mock_google.authorize_access_token.return_value = mock_token
        mock_google.get.return_value = mock_response

        mock_existing_user = Mock()
        mock_existing_user.id = 456
        mock_get_user.return_value = mock_existing_user  # User exists

        with app.test_client() as client:
            response = client.get("/auth/authorize")

        # Verify the flow
        mock_google.authorize_access_token.assert_called_once()
        mock_get_user.assert_called_once_with("existing@example.com")
        mock_login_user.assert_called_once_with(mock_existing_user)

        assert response.status_code == 302  # Redirect after login

    @patch("website.views.auth_views.logout_user")
    def test_logout_clears_session_and_redirects(self, mock_logout_user, app, app_ctx):
        """Test that logout clears session and redirects to auth page."""
        with app.test_client() as client:
            # Simulate logged in user
            with client.session_transaction() as sess:
                sess[USER_KEY] = 123

            # Mock being logged in for the @login_required decorator
            with patch("flask_login.utils._get_user") as mock_get_user:
                mock_user = Mock()
                mock_user.is_authenticated = True
                mock_get_user.return_value = mock_user

                response = client.get("/auth/logout")

        mock_logout_user.assert_called_once()
        assert response.status_code == 302  # Redirect
        assert response.location.endswith(AUTH_PREFIX)


class TestUserManagement:
    """Test user creation and lookup functions."""

    def test_get_user_returns_existing_user(self, app_ctx):
        """Test that get_user returns an existing user by email."""
        # Create a test user
        test_user = User(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            profile_picture="http://example.com/pic.jpg",
            role=UserRole.STUDENT,
        )
        test_user.save()

        # Test the function
        found_user = get_user("test@example.com")

        assert found_user is not None
        assert found_user.email == "test@example.com"
        assert found_user.first_name == "Test"

    def test_get_user_returns_none_for_nonexistent_user(self, app_ctx):
        """Test that get_user returns None for non-existent email."""
        result = get_user("nonexistent@example.com")
        assert result is None

    def test_create_new_user_with_regular_email(self, app_ctx, patcher):
        """Test creating a new user with non-admin email."""
        patcher(
            os,
            "getenv",
            lambda key, default=None: {DEFAULT_ADMIN_EMAIL: "admin@example.com"}.get(
                key, default
            ),
        )

        google_user_data = {
            GOOGLE_USER_EMAIL: "regular@example.com",
            GOOGLE_USER_GIVEN_NAME: "Regular",
            GOOGLE_USER_FAMILY_NAME: "User",
            GOOGLE_USER_PICTURE: "http://example.com/pic.jpg",
        }

        new_user = create_new_user(google_user_data)

        assert new_user is not None
        assert new_user.email == "regular@example.com"
        assert new_user.first_name == "Regular"
        assert new_user.last_name == "User"
        assert new_user.profile_picture == "http://example.com/pic.jpg"
        assert new_user.role == UserRole.INVALID  # Non-admin gets INVALID role

    def test_create_new_user_with_admin_email(self, app_ctx, patcher):
        """Test creating a new user with admin email gets admin role."""
        admin_email = "admin@example.com"
        patcher(
            os,
            "getenv",
            lambda key, default=None: {DEFAULT_ADMIN_EMAIL: admin_email}.get(
                key, default
            ),
        )

        google_user_data = {
            GOOGLE_USER_EMAIL: admin_email,
            GOOGLE_USER_GIVEN_NAME: "Admin",
            GOOGLE_USER_FAMILY_NAME: "User",
            GOOGLE_USER_PICTURE: "http://example.com/pic.jpg",
        }

        new_user = create_new_user(google_user_data)

        assert new_user is not None
        assert new_user.email == admin_email
        assert new_user.first_name == "Admin"
        assert new_user.last_name == "User"
        assert new_user.profile_picture == "http://example.com/pic.jpg"
        assert new_user.role == UserRole.ADMIN  # Admin email gets ADMIN role

    def test_create_new_user_with_missing_admin_env(self, app_ctx, patcher):
        """Test creating user when DEFAULT_ADMIN_EMAIL env var is not set."""
        patcher(os, "getenv", lambda key, default=None: None)

        google_user_data = {
            GOOGLE_USER_EMAIL: "user@example.com",
            GOOGLE_USER_GIVEN_NAME: "Test",
            GOOGLE_USER_FAMILY_NAME: "User",
            GOOGLE_USER_PICTURE: "http://example.com/pic.jpg",
        }

        new_user = create_new_user(google_user_data)

        assert new_user is not None
        assert new_user.role == UserRole.INVALID  # Should default to INVALID


class TestAuthenticationFlow:
    """Integration tests for complete authentication flows."""

    @patch("website.views.auth_views.google")
    def test_complete_login_flow_new_user(self, mock_google, app, app_ctx, patcher):
        """Test complete login flow for a new user from start to finish."""
        # Setup environment
        patcher(
            os,
            "getenv",
            lambda key, default=None: {DEFAULT_ADMIN_EMAIL: "admin@example.com"}.get(
                key, default
            ),
        )

        # Setup Google OAuth mocks
        mock_token = {"access_token": "test_token"}
        mock_google_user_data = {
            GOOGLE_USER_EMAIL: "newuser@example.com",
            GOOGLE_USER_GIVEN_NAME: "New",
            GOOGLE_USER_FAMILY_NAME: "User",
            GOOGLE_USER_PICTURE: "http://example.com/pic.jpg",
        }
        mock_response = Mock()
        mock_response.json.return_value = mock_google_user_data

        mock_google.authorize_access_token.return_value = mock_token
        mock_google.get.return_value = mock_response
        mock_google.authorize_redirect.return_value = "redirect_response"

        with app.test_client() as client:
            # Step 1: Start login flow
            with patch("website.views.auth_views.google", mock_google):
                login_response = client.get("/auth/login")

            # Step 2: Complete OAuth callback (authorize)
            with patch("flask_login.login_user") as mock_login_user:
                auth_response = client.get("/auth/authorize")

            # Verify user was created and logged in
            created_user = get_user("newuser@example.com")
            assert created_user is not None
            assert created_user.email == "newuser@example.com"
            assert created_user.role == UserRole.INVALID

    def test_logout_requires_authentication(self, app, app_ctx):
        """Test that logout route requires user to be logged in."""
        with app.test_client() as client:
            # Try to access logout without being logged in
            response = client.get("/auth/logout")

        # Should redirect to login (401 or redirect to auth)
        assert response.status_code in [302, 401]


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_create_user_with_empty_admin_email_env(self, app_ctx, patcher):
        """Test user creation when admin email env var is empty string."""
        patcher(os, "getenv", lambda key, default=None: "")

        google_user_data = {
            GOOGLE_USER_EMAIL: "user@example.com",
            GOOGLE_USER_GIVEN_NAME: "Test",
            GOOGLE_USER_FAMILY_NAME: "User",
            GOOGLE_USER_PICTURE: "http://example.com/pic.jpg",
        }

        new_user = create_new_user(google_user_data)

        assert new_user.role == UserRole.INVALID

    @patch("website.views.auth_views.google")
    def test_authorize_with_oauth_error(self, mock_google, app, app_ctx):
        """Test authorize route handles OAuth errors gracefully."""
        # Simulate OAuth error
        mock_google.authorize_access_token.side_effect = Exception("OAuth error")

        with app.test_client() as client:
            # Flask catches the exception and returns a 500 error response
            response = client.get("/auth/authorize")

        # Should return a 500 internal server error
        assert response.status_code == 500

    def test_user_creation_persistence(self, app_ctx, patcher):
        """Test that created users are properly persisted to database."""
        patcher(
            os,
            "getenv",
            lambda key, default=None: {DEFAULT_ADMIN_EMAIL: "admin@example.com"}.get(
                key, default
            ),
        )

        google_user_data = {
            GOOGLE_USER_EMAIL: "persistent@example.com",
            GOOGLE_USER_GIVEN_NAME: "Persistent",
            GOOGLE_USER_FAMILY_NAME: "User",
            GOOGLE_USER_PICTURE: "http://example.com/pic.jpg",
        }

        # Create user
        created_user = create_new_user(google_user_data)
        user_id = created_user.id

        # Verify it can be retrieved
        retrieved_user = get_user("persistent@example.com")
        assert retrieved_user is not None
        assert retrieved_user.id == user_id

        # Verify it's in the database using the updated method
        from website import db

        db_user = db.session.get(User, user_id)
        assert db_user is not None
        assert db_user.email == "persistent@example.com"
