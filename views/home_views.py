from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import db, Item, User, Tag, Location, item_tags
from sqlalchemy.orm import joinedload
from constants import (
    HOME_TEMPLATE,
    
)


home_blueprint = Blueprint('home', __name__, template_folder='../templates')

@home_blueprint.route('/', methods=['GET'])
@login_required
def home():
    items = Item.query.options(
        joinedload(Item.tags),
        joinedload(Item.location)
    ).order_by(Item.last_updated.desc()).all()

    return render_template(HOME_TEMPLATE, items=items)
