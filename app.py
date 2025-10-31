from flask import Flask

# from models import db
from views import auth_blueprint, home_blueprint, init_oauth
from constants import  AUTH_PREFIX, HOME_PREFIX, SECRET_KEY

import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv(SECRET_KEY)

# db.init_app(app)

init_oauth(app)


app.register_blueprint(auth_blueprint, url_prefix=AUTH_PREFIX)
app.register_blueprint(home_blueprint, url_prefix=HOME_PREFIX)

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()  # Create database tables
    app.run(debug=True)
