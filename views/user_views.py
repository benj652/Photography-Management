"""
Auth views
"""

from flask import Blueprint, render_template
from constants import LOGIN_ROUTE, LOGIN_TEMPLATE, USER_BLUEPRINT_NAME

user_blueprint = Blueprint(USER_BLUEPRINT_NAME, __name__)


@user_blueprint.route(LOGIN_ROUTE)
def login():
    return render_template(LOGIN_TEMPLATE)
