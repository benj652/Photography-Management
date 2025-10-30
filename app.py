from flask import Flask

# from models import db
from views import user_blueprint
from constants import USER_PREFIX

app = Flask(__name__)

# db.init_app(app)


app.register_blueprint(user_blueprint, url_prefix=USER_PREFIX)

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()  # Create database tables
    app.run(debug=True)
