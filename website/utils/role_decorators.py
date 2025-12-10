"""
=========================================
Standard user roles promissions.
=========================================

ADMIN: Below permissions and Has full access to all resources and can manage other users.
TA: Below permissions Can view and modify resources but cannot manage users.
STUDENT: Below permissions can only view resources and check out equipment.
INVALID: Student not in Photography who can not see or edit the database at all.
"""


from functools import wraps
from flask_login import current_user
from flask import abort
from ..constants import ERROR_NOT_AUTHORIZED, UserRole


def require_approved(f):
    """Require that the current user is approved (admin/TA/student).

    This wraps a view and returns 403 if the user's role is not one of the
    allowed roles.
    """
    return require_roles([UserRole.ADMIN, UserRole.TA, UserRole.STUDENT])(f)

def require_ta(f):
    """Require that the current user is a TA or admin."""
    return require_roles([UserRole.ADMIN, UserRole.TA])(f)

def require_admin(f):
    """Require that the current user is an admin."""
    return require_roles([UserRole.ADMIN])(f)

def require_roles(roles: list[UserRole]):
    """Return a decorator that ensures the current user has one of `roles`."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(ERROR_NOT_AUTHORIZED)
            if current_user.role not in roles:
                abort(ERROR_NOT_AUTHORIZED)
            return f(*args, **kwargs)

        return decorated_function

    return decorator
