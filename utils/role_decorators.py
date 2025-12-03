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

from constants import ERROR_NOT_AUTHORIZED, UserRole
from flask_login import current_user
from flask import abort


def require_approved(f):
    return require_roles([UserRole.ADMIN, UserRole.TA, UserRole.STUDENT])(f)

def require_ta(f):
    return require_roles([UserRole.ADMIN, UserRole.TA])(f)

def require_admin(f):
    return require_roles([UserRole.ADMIN])(f)

def require_roles(roles: list[UserRole]):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.role not in roles:
                abort(ERROR_NOT_AUTHORIZED)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
