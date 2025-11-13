'''
Decorator functions for roles
'''

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
