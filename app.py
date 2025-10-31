from flask import Flask, url_for, session, redirect
from authlib.integrations.flask_client import OAuth

# from models import db
from views import user_blueprint
from constants import USER_PREFIX

import os

from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECERET_KEY")

# db.init_app(app)


oauth = OAuth(app)

google = oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    client_kwargs={'scope': 'openid email profile'},
    userinfo_endpoint='https://www.googleapis.com/oauth2/v1/userinfo'
)

@app.route('/')
def index():
    user = session.get('user')
    if user:
        return f"Hello, {user['name']}! <a href='/logout'>Logout</a>"
    return "<a href='/login'>Login with Google</a>"

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('https://www.googleapis.com/oauth2/v1/userinfo', token=token)
    user = resp.json()
    session['user'] = user
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')


app.register_blueprint(user_blueprint, url_prefix=USER_PREFIX)

if __name__ == "__main__":
    # with app.app_context():
    #     db.create_all()  # Create database tables
    app.run(debug=True)
