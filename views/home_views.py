from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from models import db, Item, User, Tag, Location, item_tags
from sqlalchemy.orm import joinedload
from constants import(
    ITEM_FIELD_ID,
    ITEM_FIELD_NAME,
    ITEM_FIELD_QUANTITY,
    ITEM_FIELD_TAGS,
    ITEM_FIELD_LOCATION_ID,
    ITEM_FIELD_EXPIRES,
    ITEM_FIELD_LAST_UPDATED,
    ITEM_FIELD_UPDATED_BY,
    HOME_TEMPLATE,
    HOME_BLUEPRINT_NAME
    )


home_blueprint = Blueprint(HOME_BLUEPRINT_NAME, __name__)


@home_blueprint.route('/', methods=['GET'])
@login_required
def home():
    """Render the home page.

    If SQLAlchemy is configured, query real items from the DB and convert them
    into the simple dict shape expected by the template. Otherwise fall back
    to the static mock data already used during development.
    """
    items_list = []

    q = Item.query.options(joinedload(Item.tags), 
                            joinedload(Item.location),
                            joinedload(Item.updated_by_user))
    items = q.all()
    
    for it in items:
        tags = ', '.join([t.name for t in getattr(it, ITEM_FIELD_TAGS, [])])
        loc = getattr(it, 'location', None)
        location_name = loc.name if loc else None
        updater = None
        if it.updated_by_user:
            updater = it.updated_by_user.email
        elif it.updated_by:
            updater = str(it.updated_by)

        items_list.append({
            ITEM_FIELD_ID: it.id,
            ITEM_FIELD_NAME: it.name,
            ITEM_FIELD_QUANTITY: it.quantity,
            ITEM_FIELD_TAGS: tags,
            'location': location_name, #unsure what to replace this magic string with. ITEM_FIELD_LOCATION_ID doesnt seem correct
            ITEM_FIELD_EXPIRES: it.expires.isoformat() if it.expires else '—',
            ITEM_FIELD_LAST_UPDATED: it.last_updated.strftime('%Y-%m-%d %H:%M') if it.last_updated else '—',
            ITEM_FIELD_UPDATED_BY: updater,
        })

    current_app.logger.debug(f'Current user: {current_user}')
    return render_template(HOME_TEMPLATE, items=items_list)
