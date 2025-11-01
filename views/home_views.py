from flask import Blueprint, render_template
from flask_login import login_required, current_user


home_blueprint = Blueprint('home', __name__)

@home_blueprint.route('/')
#@login_required
def home():
    print(f"Current user: {current_user}")
    return render_template('home.html')
