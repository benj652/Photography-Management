from flask import Flask, redirect, url_for
from flask_login import LoginManager

from models import db, User
from views import (
    auth_blueprint,
    home_blueprint,
    item_blueprint,
    init_oauth,
    tags_blueprint,
)
from constants import (
    AUTH_PREFIX,
    HOME_PREFIX,
    ITEM_PREFIX,
    NOT_FOUND_ROUTE,
    SECRET_KEY,
    SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_TRACK_MODIFICATIONS,
    TAG_PREFIX,
)

import os

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(SECRET_KEY)
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
app.register_blueprint(item_blueprint, url_prefix=ITEM_PREFIX)
app.register_blueprint(tags_blueprint, url_prefix=TAG_PREFIX)


@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for(NOT_FOUND_ROUTE))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
