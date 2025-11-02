"""Item views: provide API endpoints to list and create items.

This blueprint exposes:
- GET /items/      -> list items (JSON)
- POST /items/     -> create an item (JSON or form)

When the app is running without a database configured, the endpoints
will return an empty list or redirect appropriately to avoid 500s.
"""

from flask import Blueprint, jsonify, request, current_app, redirect, url_for
from flask_login import current_user
from models import db, Item, Tag, Location, User
from sqlalchemy.orm import joinedload
from datetime import datetime


item_blueprint = Blueprint('item', __name__)


def item_to_dict(item: Item) -> dict:
	# convert Item to serializable dict, resolving tags and location
	tags = [t.name for t in item.tags] if getattr(item, 'tags', None) else []
	try:
		location_name = item.location.name if getattr(item, 'location', None) else None
	except Exception:
		# relationship may not be configured; try to load by id
		location_name = None
	updater_email = None
	try:
		if item.updated_by:
			user = User.query.get(item.updated_by)
			if user:
				updater_email = user.email
	except Exception:
		updater_email = None

	return {
		'id': item.id,
		'name': item.name,
		'quantity': item.quantity,
		'tags': tags,
		'location': location_name,
		'expires': item.expires.isoformat() if item.expires else None,
		'last_updated': item.last_updated.isoformat() if item.last_updated else None,
		'updated_by': updater_email or item.updated_by,
	}


@item_blueprint.route('/', methods=['GET'])
def get_items():
	"""Return JSON array of items."""
	if 'sqlalchemy' not in current_app.extensions:
		return jsonify([])

	items = Item.query.options(joinedload(Item.tags)).all()
	return jsonify([item_to_dict(i) for i in items])


@item_blueprint.route('/', methods=['POST'])
def create_item():
	"""Create an Item from JSON or form data. Returns the created item as JSON.

	Expected fields (JSON or form): name (required), quantity, tags (comma-separated),
	location_id, expires (YYYY-MM-DD), updated_by (user id)
	"""
	if 'sqlalchemy' not in current_app.extensions:
		return jsonify({'error': 'database not configured'}), 503

	data = request.get_json(silent=True) or request.form
	name = data.get('name')
	if not name:
		return jsonify({'error': 'name is required'}), 400

	try:
		quantity = int(data.get('quantity') or 1)
	except Exception:
		quantity = 1

	expires = None
	expires_raw = data.get('expires')
	if expires_raw:
		try:
			expires = datetime.strptime(expires_raw, '%Y-%m-%d').date()
		except Exception:
			expires = None

	location = None
	location_id = data.get('location_id') or data.get('location')
	if location_id:
		try:
			location = Location.query.get(int(location_id))
		except Exception:
			location = None

	# Use the logged-in user's id for the updater when available.
	# Do NOT accept an updated_by value from unauthenticated clients.
	updated_by = None
	if getattr(current_user, 'is_authenticated', False):
		try:
			updated_by = int(current_user.id)
		except Exception:
			updated_by = None

	item = Item(
		name=name,
		quantity=quantity,
		location_id=location.id if location else None,
		expires=expires,
		last_updated=datetime.utcnow(),
		updated_by=updated_by,
	)

	# tags handling
	tags_raw = data.get('tags')
	if tags_raw:
		if isinstance(tags_raw, str):
			tag_names = [t.strip() for t in tags_raw.split(',') if t.strip()]
		elif isinstance(tags_raw, (list, tuple)):
			tag_names = [str(t).strip() for t in tags_raw if str(t).strip()]
		else:
			tag_names = []

		# Fetch all existing tags in a single query
		existing_tags = {t.name: t for t in Tag.query.filter(Tag.name.in_(tag_names)).all()}
		for tn in tag_names:
			tag = existing_tags.get(tn)
			if not tag:
				tag = Tag(name=tn)
				db.session.add(tag)
				existing_tags[tn] = tag
			item.tags.append(tag)
	db.session.add(item)
	db.session.commit()

	# If the request was a regular form POST (not JSON), redirect back to
	# the home page so the browser doesn't show raw JSON.
	if not request.is_json:
		return redirect(url_for('home.home'))

	return jsonify(item_to_dict(item)), 201

