from flask import Flask, redirect, render_template, url_for
from flask_login import LoginManager

from models import db, User, Consumable
from views import (
    auth_blueprint,
    home_blueprint,
    item_blueprint,
    init_oauth,
    tags_blueprint,
    location_blueprint,
    admin_blueprint,
    lab_equipment_blueprint,
    camera_gear_blueprint,
    consumables_blueprint,
)
from constants import (
    ADMIN_PREFIX,
    ADMIN_TEMPLATE,
    API_PREFIX,
    AUTH_PREFIX,
    CAMERA_GEAR_PREFIX,
    ERROR_NOT_AUTHORIZED,
    ERROR_NOT_FOUND,
    HOME_PREFIX,
    ITEM_PREFIX,
    LAB_EQUIPMENT_PREFIX,
    LOCATION_PREFIX,
    NOT_FOUND_ROUTE,
    SECRET_KEY,
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    TAG_PREFIX,
    UNAUTHORIZED_TEMPLATE,
    CONSUMABLES_PREFIX,
)

import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(SECRET_KEY)
if os.environ.get('CLOUD'): # check if cloud deployment
    app.config[SQLALCHEMY_DATABASE_URI] = os.environ.get('DATABASE_URL').replace("postgres", "postgresql", 1)
else:
    app.config[SQLALCHEMY_DATABASE_URI] = os.getenv(SQLALCHEMY_DATABASE_URI)
app.config[SQLALCHEMY_TRACK_MODIFICATIONS] = os.getenv(SQLALCHEMY_TRACK_MODIFICATIONS)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = AUTH_PREFIX


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


db.init_app(app)

init_oauth(app)


app.register_blueprint(auth_blueprint, url_prefix=AUTH_PREFIX)
app.register_blueprint(home_blueprint, url_prefix=HOME_PREFIX)
app.register_blueprint(admin_blueprint, url_prefix=ADMIN_PREFIX)
app.register_blueprint(item_blueprint, url_prefix=API_PREFIX + ITEM_PREFIX)
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


@app.errorhandler(ERROR_NOT_FOUND)
def page_not_found(e):
    return redirect(url_for(NOT_FOUND_ROUTE))


@app.errorhandler(ERROR_NOT_AUTHORIZED)
def not_authorized(e):
    return render_template(UNAUTHORIZED_TEMPLATE)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
