"""Application entrypoint and Flask app configuration.

This module creates the Flask application, configures extensions (DB,
login, mail) and registers blueprints. Changes here should be limited to
configuration and wiring only.
"""

import os

from dotenv import load_dotenv
from flask import Flask, redirect, render_template, url_for
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .models import User
from .views import (
    auth_blueprint,
    home_blueprint,
    init_oauth,
    tags_blueprint,
    location_blueprint,
    admin_blueprint,
    lab_equipment_blueprint,
    camera_gear_blueprint,
    consumables_blueprint,
    tasks_blueprint,
    notes_blueprint,
)
from .constants import (
    ADMIN_PREFIX,
    API_PREFIX,
    AUTH_PREFIX,
    CAMERA_GEAR_PREFIX,
    ERROR_NOT_AUTHORIZED,
    ERROR_NOT_FOUND,
    HOME_PREFIX,
    LAB_EQUIPMENT_PREFIX,
    LOCATION_PREFIX,
    NOT_FOUND_ROUTE,
    SECRET_KEY,
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    TAG_PREFIX,
    UNAUTHORIZED_TEMPLATE,
    CONSUMABLES_PREFIX,
    NOTES_PREFIX,
)

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.secret_key = os.getenv(SECRET_KEY)
    if os.environ.get("CLOUD"):  # check if cloud deployment
        db_url = os.environ.get("DATABASE_URL")
        if db_url and db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        app.config[SQLALCHEMY_DATABASE_URI] = db_url
    else:
        app.config[SQLALCHEMY_DATABASE_URI] = os.getenv(SQLALCHEMY_DATABASE_URI)
        if not app.config[SQLALCHEMY_DATABASE_URI]:
            app.config[SQLALCHEMY_DATABASE_URI] = "sqlite:///photography.db"

    # Keep the SQLAlchemy option as a boolean-like environment value if present.
    app.config[SQLALCHEMY_TRACK_MODIFICATIONS] = os.getenv(SQLALCHEMY_TRACK_MODIFICATIONS)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = AUTH_PREFIX
    login_manager.login_message = None


    @login_manager.user_loader
    def load_user(user_id):
        """Load a user by ID for flask-login.

        Returns ``None`` when the user isn't found.
        """
        return User.query.get(int(user_id))


    db.init_app(app)

    # Mail configuration - read common mail-related env vars. If not present, Mail initialization will still
    # occur but sending will be a no-op until valid settings are provided in env.
    app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
    _mail_port = os.getenv("MAIL_PORT")
    app.config["MAIL_PORT"] = int(_mail_port) if _mail_port else None
    app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
    app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
    app.config["MAIL_DEFAULT_SENDER"] = os.getenv(
        "MAIL_DEFAULT_SENDER", os.getenv("DEFAULT_ADMIN_EMAIL")
    )

    # Normalize mail TLS/SSL env values to booleans in a short, readable form.
    _mail_tls = os.getenv("MAIL_USE_TLS", "True").lower()
    app.config["MAIL_USE_TLS"] = _mail_tls in ("1", "true", "yes")
    _mail_ssl = os.getenv("MAIL_USE_SSL", "False").lower()
    app.config["MAIL_USE_SSL"] = _mail_ssl in ("1", "true", "yes")

    init_oauth(app)

#   Initialize the mail helper (flask-mailman)
    try:
        from utils.mail import init_mail

        init_mail(app)
    except Exception:
        # don't crash app if mail isn't available; emails will be a no-op
        pass


    app.register_blueprint(auth_blueprint, url_prefix=AUTH_PREFIX)
    app.register_blueprint(home_blueprint, url_prefix=HOME_PREFIX)
    app.register_blueprint(admin_blueprint, url_prefix=ADMIN_PREFIX)
    app.register_blueprint(
        camera_gear_blueprint, url_prefix=API_PREFIX + CAMERA_GEAR_PREFIX
    )
    app.register_blueprint(
        lab_equipment_blueprint, url_prefix=API_PREFIX + LAB_EQUIPMENT_PREFIX
    )
    app.register_blueprint(
        consumables_blueprint, url_prefix=API_PREFIX + CONSUMABLES_PREFIX
    )
    app.register_blueprint(tags_blueprint, url_prefix=API_PREFIX + TAG_PREFIX)
    app.register_blueprint(location_blueprint, url_prefix=API_PREFIX + LOCATION_PREFIX)
    app.register_blueprint(tasks_blueprint)
    app.register_blueprint(notes_blueprint, url_prefix=API_PREFIX + NOTES_PREFIX)

    @app.errorhandler(ERROR_NOT_FOUND)
    def page_not_found(e):
        """Redirect to the configured not-found route.

        The argument is provided by Flask's error handler API but is not
        used here.
        """
        # pylint: disable=unused-argument
        return redirect(url_for(NOT_FOUND_ROUTE))


    @app.errorhandler(ERROR_NOT_AUTHORIZED)
    def not_authorized(e):
        """Render the unauthorized template for 403 responses.

        The error argument is required by Flask but not consumed.
        """
        # pylint: disable=unused-argument
        # return with the proper 403 status code so callers (and tests) can
        # detect the unauthorized response programmatically.
        return render_template(UNAUTHORIZED_TEMPLATE), ERROR_NOT_AUTHORIZED


    with app.app_context():
        db.create_all()  # Create database tables

    return app
