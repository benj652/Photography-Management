from flask import Flask, url_for, session, redirect
from authlib.integrations.flask_client import OAuth

# from models import db
from views import auth_blueprint, home_blueprint
from constants import  AUTH_PREFIX

import os

from dotenv import load_dotenv

from views.auth_views import init_oauth
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECERET_KEY")

# db.init_app(app)

init_oauth(app)


app.register_blueprint(auth_blueprint, url_prefix=AUTH_PREFIX)
app.register_blueprint(home_blueprint, url_prefix='/home')

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()  # Create database tables
    app.run(debug=True)
