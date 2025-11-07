from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, User
from views import (
    auth_blueprint,
    home_blueprint,
    item_blueprint,
    init_oauth,
    tags_blueprint,
    location_blueprint
)
from constants import (
    AUTH_PREFIX,
    HOME_PREFIX,
    ITEM_PREFIX,
    LOCATION_PREFIX,
    NOT_FOUND_ROUTE,
    TAG_PREFIX,
)

import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# DEBUG: Show what we got
print("URI from .env:", repr(os.getenv('SQLALCHEMY_DATABASE_URI')))

app = Flask(__name__)

# HARD-CODED FALLBACK — this prevents crash if .env fails
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.getenv('SQLALCHEMY_DATABASE_URI') or 'sqlite:///inventory.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or 'dev-secret-key'

# Initialize extensions
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = AUTH_PREFIX

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize DB and OAuth
db.init_app(app)
init_oauth(app)

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix=AUTH_PREFIX)
app.register_blueprint(home_blueprint, url_prefix=HOME_PREFIX)
app.register_blueprint(item_blueprint, url_prefix=ITEM_PREFIX)
app.register_blueprint(tags_blueprint, url_prefix=TAG_PREFIX)
app.register_blueprint(location_blueprint, url_prefix=LOCATION_PREFIX)

# 404 handler
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for(NOT_FOUND_ROUTE))

# Run app
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates inventory.db if missing
        print("Database ready: inventory.db")
    app.run(debug=True)