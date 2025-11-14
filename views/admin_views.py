"""
Admin Views
"""

from flask import Blueprint, render_template

from constants import ADMIN_TEMPLATE, GET, POST, UserRole
from models import User
from utils.role_decorators import require_admin


admin_blueprint = Blueprint("admin", __name__)

@admin_blueprint.route("/dashboard")
@require_admin
def dashboard():
    return render_template(ADMIN_TEMPLATE)

@admin_blueprint.route("/users/all", methods=[GET])
@require_admin
def get_all_users():
    users = User.query.all()
    return {
        "user" : [user.to_dict() for user in users]
    }



@admin_blueprint.route("/users/to-admin/<int:user_id>", methods=[POST])
@require_admin
def make_admin(user_id: int):
    user = User.query.get_or_404(user_id)
    user.role = UserRole.ADMIN
    user.save()
    return user.to_dict()

@admin_blueprint.route("/users/to-student/<int:user_id>", methods=[POST])
@require_admin
def make_student(user_id: int):
    user = User.query.get_or_404(user_id)
    user.role = UserRole.STUDENT
    user.save()
    return user.to_dict()

@admin_blueprint.route("/users/to-ta/<int:user_id>", methods=[POST])
@require_admin
def make_ta(user_id: int):
    user = User.query.get_or_404(user_id)
    user.role = UserRole.TA
    user.save()
    return user.to_dict()

@admin_blueprint.route("/users/to-invalid/<int:user_id>", methods=[POST])
@require_admin
def make_invalid(user_id: int):
    user = User.query.get_or_404(user_id)
    user.role = UserRole.INVALID
    user.save()
    return user.to_dict()
