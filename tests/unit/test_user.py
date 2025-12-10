"""Unit tests for the User model.

This module tests the User SQLAlchemy model including:
- User creation and validation
- Database operations (save, query)
- Model methods (to_dict, __repr__)
- Flask-Login integration
- Role management
- Edge cases and error conditions
"""

import pytest
from sqlalchemy.exc import IntegrityError
from website.models.user import User
from website.constants import UserRole
from website import db


class TestUserModel:
    """Test basic User model functionality."""
    
    def test_user_creation_with_all_fields(self, app_ctx):
        """Test creating a user with all fields populated."""
        user = User(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            profile_picture="https://example.com/profile.jpg",
            role=UserRole.STUDENT
        )
        
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.email == "john.doe@example.com"
        assert user.profile_picture == "https://example.com/profile.jpg"
        assert user.role == UserRole.STUDENT
        assert user.id is None  # Not saved to database yet
    
    def test_user_creation_with_minimal_fields(self, app_ctx):
        """Test creating a user with only required fields."""
        user = User(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            role=UserRole.TA
        )
        
        assert user.first_name == "Jane"
        assert user.last_name == "Smith"
        assert user.email == "jane.smith@example.com"
        assert user.profile_picture is None  # Optional field
        assert user.role == UserRole.TA
    
    def test_user_creation_with_different_roles(self, app_ctx):
        """Test creating users with different role types."""
        roles_to_test = [
            UserRole.ADMIN,
            UserRole.TA,
            UserRole.STUDENT,
            UserRole.INVALID
        ]
        
        for role in roles_to_test:
            user = User(
                first_name="Test",
                last_name="User",
                email=f"test_{role.value}@example.com",
                role=role
            )
            assert user.role == role


class TestUserDatabaseOperations:
    """Test User database operations."""
    
    def test_user_save_method(self, app_ctx):
        """Test the user save method persists to database."""
        user = User(
            first_name="Alice",
            last_name="Johnson",
            email="alice.johnson@example.com",
            profile_picture="https://example.com/alice.jpg",
            role=UserRole.ADMIN
        )
        
        # User should not have ID before saving
        assert user.id is None
        
        # Save user
        user.save()
        
        # User should now have ID after saving
        assert user.id is not None
        assert isinstance(user.id, int)
        
        # Verify user can be retrieved from database
        retrieved_user = User.query.filter_by(email="alice.johnson@example.com").first()
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.first_name == "Alice"
        assert retrieved_user.last_name == "Johnson"
        assert retrieved_user.email == "alice.johnson@example.com"
        assert retrieved_user.role == UserRole.ADMIN
    
    def test_user_email_uniqueness_constraint(self, app_ctx):
        """Test that email uniqueness constraint is enforced."""
        # Create and save first user
        user1 = User(
            first_name="First",
            last_name="User",
            email="duplicate@example.com",
            role=UserRole.STUDENT
        )
        user1.save()
        
        # Try to create second user with same email
        user2 = User(
            first_name="Second",
            last_name="User",
            email="duplicate@example.com",  # Same email
            role=UserRole.TA
        )
        
        # Should raise IntegrityError when trying to save
        with pytest.raises(IntegrityError):
            user2.save()
    
    def test_user_query_operations(self, app_ctx):
        """Test various user query operations."""
        # Create multiple users
        users_data = [
            ("Admin", "User", "admin@example.com", UserRole.ADMIN),
            ("Student", "One", "student1@example.com", UserRole.STUDENT),
            ("Student", "Two", "student2@example.com", UserRole.STUDENT),
            ("TA", "User", "ta@example.com", UserRole.TA),
        ]
        
        created_users = []
        for first, last, email, role in users_data:
            user = User(
                first_name=first,
                last_name=last,
                email=email,
                role=role
            )
            user.save()
            created_users.append(user)
        
        # Test query all users
        all_users = User.query.all()
        assert len(all_users) == 4
        
        # Test filter by role
        students = User.query.filter_by(role=UserRole.STUDENT).all()
        assert len(students) == 2
        
        # Test filter by email
        admin_user = User.query.filter_by(email="admin@example.com").first()
        assert admin_user is not None
        assert admin_user.role == UserRole.ADMIN
        
        # Test get by ID
        user_id = created_users[0].id
        user_by_id = db.session.get(User, user_id)
        assert user_by_id is not None
        assert user_by_id.email == "admin@example.com"


class TestUserMethods:
    """Test User model methods."""
    
    def test_to_dict_method_complete_user(self, app_ctx):
        """Test to_dict method with all fields populated."""
        user = User(
            first_name="Bob",
            last_name="Wilson",
            email="bob.wilson@example.com",
            profile_picture="https://example.com/bob.jpg",
            role=UserRole.TA
        )
        user.save()
        
        user_dict = user.to_dict()
        
        assert isinstance(user_dict, dict)
        assert user_dict["id"] == user.id
        assert user_dict["first_name"] == "Bob"
        assert user_dict["last_name"] == "Wilson"
        assert user_dict["email"] == "bob.wilson@example.com"
        assert user_dict["profile_picture"] == "https://example.com/bob.jpg"
        assert user_dict["role"] == UserRole.TA.value
    
    def test_to_dict_method_minimal_user(self, app_ctx):
        """Test to_dict method with minimal fields."""
        user = User(
            first_name="Carol",
            last_name="Brown",
            email="carol.brown@example.com",
            role=UserRole.STUDENT
        )
        user.save()
        
        user_dict = user.to_dict()
        
        assert user_dict["first_name"] == "Carol"
        assert user_dict["last_name"] == "Brown"
        assert user_dict["email"] == "carol.brown@example.com"
        assert user_dict["profile_picture"] is None
        assert user_dict["role"] == UserRole.STUDENT.value
    
    def test_to_dict_method_with_none_role(self, app_ctx):
        """Test to_dict method when role is None."""
        user = User(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            role=UserRole.INVALID
        )
        # Manually set role to None to test edge case
        user.role = None
        
        user_dict = user.to_dict()
        assert user_dict["role"] is None
    
    def test_repr_method(self, app_ctx):
        """Test __repr__ method returns expected format."""
        user = User(
            first_name="David",
            last_name="Miller",
            email="david.miller@example.com",
            role=UserRole.ADMIN
        )
        
        repr_str = repr(user)
        expected = f"<User david.miller@example.com Role {UserRole.ADMIN}>"
        assert repr_str == expected
    
    def test_repr_method_with_different_roles(self, app_ctx):
        """Test __repr__ method with different user roles."""
        roles_to_test = [
            UserRole.ADMIN,
            UserRole.TA,
            UserRole.STUDENT,
            UserRole.INVALID
        ]
        
        for role in roles_to_test:
            user = User(
                first_name="Test",
                last_name="User",
                email=f"test_{role.value}@example.com",
                role=role
            )
            
            repr_str = repr(user)
            expected = f"<User test_{role.value}@example.com Role {role}>"
            assert repr_str == expected


class TestFlaskLoginIntegration:
    """Test Flask-Login UserMixin integration."""
    
    def test_user_inherits_from_usermixin(self, app_ctx):
        """Test that User class inherits from UserMixin."""
        from flask_login import UserMixin
        
        user = User(
            first_name="Login",
            last_name="Test",
            email="login.test@example.com",
            role=UserRole.STUDENT
        )
        
        # Check inheritance
        assert isinstance(user, UserMixin)
    
    def test_user_has_flask_login_methods(self, app_ctx):
        """Test that User has Flask-Login required methods."""
        user = User(
            first_name="Auth",
            last_name="User",
            email="auth.user@example.com",
            role=UserRole.TA
        )
        user.save()
        
        # Test UserMixin methods are available
        assert hasattr(user, 'is_authenticated')
        assert hasattr(user, 'is_active')
        assert hasattr(user, 'is_anonymous')
        assert hasattr(user, 'get_id')
        
        # Test default UserMixin behavior
        assert user.is_authenticated is True
        assert user.is_active is True
        assert user.is_anonymous is False
        assert user.get_id() == str(user.id)


class TestUserValidation:
    """Test User model validation and constraints."""
    
    def test_user_creation_without_required_fields_fails(self, app_ctx):
        """Test that creating user without required fields fails."""
        # Test missing first_name - should raise IntegrityError when saving
        with pytest.raises(IntegrityError):
            User(
                last_name="Test",
                email="test1@example.com",
                role=UserRole.STUDENT
            ).save()
        
        # Rollback the session after the first error
        db.session.rollback()
        
        # Test missing email - should raise IntegrityError when saving  
        with pytest.raises(IntegrityError):
            User(
                first_name="Test",
                last_name="User",
                role=UserRole.STUDENT
            ).save()
        
        # Rollback the session after the second error
        db.session.rollback()
        
        # Test missing role - should raise IntegrityError when saving
        with pytest.raises(IntegrityError):
            User(
                first_name="Test",
                last_name="User",
                email="test2@example.com"
            ).save()
    
    def test_user_email_format_flexibility(self, app_ctx):
        """Test that various email formats are accepted."""
        valid_emails = [
            "simple@example.com",
            "test.email@domain.co.uk",
            "user+tag@subdomain.example.org",
            "123@numbers.com",
            "user_name@example-domain.com"
        ]
        
        for i, email in enumerate(valid_emails):
            user = User(
                first_name="Test",
                last_name=f"User{i}",
                email=email,
                role=UserRole.STUDENT
            )
            user.save()
            
            # Verify user was saved successfully
            saved_user = User.query.filter_by(email=email).first()
            assert saved_user is not None
            assert saved_user.email == email
    
    def test_user_string_field_lengths(self, app_ctx):
        """Test string field length constraints."""
        # Test normal length strings
        user = User(
            first_name="A" * 79,  # Just under 80 char limit
            last_name="B" * 79,
            email="test@example.com",
            profile_picture="https://example.com/" + "c" * 150,  # Just under 200 char limit
            role=UserRole.STUDENT
        )
        user.save()
        
        # Verify user was saved
        assert user.id is not None


class TestUserRoleManagement:
    """Test user role-related functionality."""
    
    def test_role_assignment_and_retrieval(self, app_ctx):
        """Test assigning and retrieving different roles."""
        users_and_roles = [
            ("admin@example.com", UserRole.ADMIN),
            ("ta@example.com", UserRole.TA),
            ("student@example.com", UserRole.STUDENT),
            ("invalid@example.com", UserRole.INVALID),
        ]
        
        created_users = []
        for email, role in users_and_roles:
            user = User(
                first_name="Test",
                last_name="User",
                email=email,
                role=role
            )
            user.save()
            created_users.append(user)
        
        # Verify roles were saved correctly
        for user, (_, expected_role) in zip(created_users, users_and_roles):
            retrieved_user = db.session.get(User, user.id)
            assert retrieved_user.role == expected_role
    
    def test_role_enum_values(self, app_ctx):
        """Test that UserRole enum values are correctly stored."""
        role_mappings = {
            UserRole.ADMIN: "admin",
            UserRole.TA: "ta",
            UserRole.STUDENT: "student",
            UserRole.INVALID: "invalid"
        }
        
        for role, expected_value in role_mappings.items():
            user = User(
                first_name="Role",
                last_name="Test",
                email=f"role_{expected_value}@example.com",
                role=role
            )
            user.save()
            
            # Test both the enum and its value
            assert user.role == role
            assert user.role.value == expected_value
            
            # Test to_dict returns the value
            user_dict = user.to_dict()
            assert user_dict["role"] == expected_value


class TestUserEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_user_with_empty_strings(self, app_ctx):
        """Test user creation with empty string values."""
        # Empty strings should be allowed for optional fields
        user = User(
            first_name="",  # Empty but not None
            last_name="",
            email="empty@example.com",
            profile_picture="",  # Empty profile picture
            role=UserRole.STUDENT
        )
        user.save()
        
        assert user.id is not None
        assert user.first_name == ""
        assert user.last_name == ""
        assert user.profile_picture == ""
    
    def test_user_with_special_characters(self, app_ctx):
        """Test user with special characters in names."""
        user = User(
            first_name="José-María",
            last_name="O'Connor-Smith",
            email="jose.maria@example.com",
            profile_picture="https://example.com/josé.jpg",
            role=UserRole.TA
        )
        user.save()
        
        retrieved_user = User.query.filter_by(email="jose.maria@example.com").first()
        assert retrieved_user.first_name == "José-María"
        assert retrieved_user.last_name == "O'Connor-Smith"
    
    def test_multiple_save_calls(self, app_ctx):
        """Test that calling save() multiple times doesn't create duplicates."""
        user = User(
            first_name="Multi",
            last_name="Save",
            email="multi.save@example.com",
            role=UserRole.STUDENT
        )
        
        # Save multiple times
        user.save()
        original_id = user.id
        user.save()
        user.save()
        
        # ID should remain the same
        assert user.id == original_id
        
        # Should only be one user with this email
        users_with_email = User.query.filter_by(email="multi.save@example.com").all()
        assert len(users_with_email) == 1
    
    def test_user_modification_after_save(self, app_ctx):
        """Test modifying user attributes after saving."""
        user = User(
            first_name="Original",
            last_name="Name",
            email="modify@example.com",
            role=UserRole.STUDENT
        )
        user.save()
        original_id = user.id
        
        # Modify attributes
        user.first_name = "Modified"
        user.role = UserRole.TA
        user.save()
        
        # Verify changes were saved
        assert user.id == original_id  # ID shouldn't change
        retrieved_user = db.session.get(User, original_id)
        assert retrieved_user.first_name == "Modified"
        assert retrieved_user.role == UserRole.TA