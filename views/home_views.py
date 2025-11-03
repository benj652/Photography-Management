from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import db, Item, User, Tag, Location, item_tags
from sqlalchemy.orm import joinedload
from constants import (
    HOME_TEMPLATE,
    FILTER_NAME,
    FILTER_TAGS,
    FILTER_LOCATION,
)


home_blueprint = Blueprint('home', __name__, template_folder='../templates')


@home_blueprint.route('/', methods=['GET'])
@login_required
def home():
    # Start with the base query 
    query = Item.query.options(
        joinedload(Item.tags),
        joinedload(Item.location)
    )

    # ---------- FILTERS ----------
    name_filter = request.args.get(FILTER_NAME)
    if name_filter:
        query = query.filter(Item.name.ilike(f"%{name_filter}%"))

    tags_filter = request.args.get(FILTER_TAGS)
    if tags_filter:
        tag_names = [t.strip() for t in tags_filter.split(',') if t.strip()]
        if tag_names:
            query = query.join(item_tags).join(Tag).filter(Tag.name.in_(tag_names))

    location_filter = request.args.get(FILTER_LOCATION)
    if location_filter:
        query = query.join(Location).filter(Location.name.ilike(f"%{location_filter}%"))

    # ---------- EXECUTE ----------
    items = query.order_by(Item.last_updated.desc()).all()

    return render_template(HOME_TEMPLATE, items=items)