from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from models import Item, User
from sqlalchemy.orm import joinedload


home_blueprint = Blueprint('home', __name__)


@home_blueprint.route('/')
#@login_required
def home():
    """Render the home page.

    If SQLAlchemy is configured, query real items from the DB and convert them
    into the simple dict shape expected by the template. Otherwise fall back
    to the static mock data already used during development.
    """
    items_list = []

    # If the app has SQLAlchemy initialized, use real DB items
    if 'sqlalchemy' in current_app.extensions:
        # load tags and location relationships eagerly
        try:
            q = Item.query.options(joinedload(Item.tags), joinedload(Item.location))
            items = q.all()
            for it in items:
                tags = ', '.join([t.name for t in getattr(it, 'tags', [])])
                loc = getattr(it, 'location', None)
                location_name = loc.name if loc else None
                updater = None
                if it.updated_by:
                    u = User.query.get(it.updated_by)
                    updater = u.email if u else it.updated_by

                items_list.append({
                    'id': it.id,
                    'name': it.name,
                    'quantity': it.quantity,
                    'tags': tags,
                    'location': location_name,
                    'expires': it.expires.isoformat() if it.expires else '—',
                    'last_updated': it.last_updated.strftime('%Y-%m-%d %H:%M') if it.last_updated else '—',
                    'updated_by': updater,
                })
        except Exception:
            # If anything goes wrong querying the DB, fall back to mock data
            items_list = []

    print(f"Current user: {current_user}")
    return render_template('home.html', items=items_list)
