# Functional tests for the consumables API endpoints
# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,too-many-lines,line-too-long,import-outside-toplevel,unused-argument,redefined-outer-name,wrong-import-order,unused-import

import json
from datetime import datetime

import pytest
import uuid

from website.constants import (
    API_PREFIX,
    CONSUMABLES_PREFIX,
    CONSUMABLES_ALL_ROUTE,
    CONSUMABLES_GET_ONE_ROUTE,
    CONSUMABLES_CREATE_ROUTE,
    CONSUMABLES_UPDATE_ROUTE,
    CONSUMABLES_DELETE_ROUTE,
    ERROR_BAD_REQUEST,
    ERROR_NOT_AUTHORIZED,
    UserRole,
)
from website.models import Consumable
from website import db

from website.models import Tag, Location


def login_user_in_client(client, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True


@pytest.fixture
def admin_user(app_ctx):
    from website.models import User

    user = User(first_name="Admin", last_name="User", email="admin@x.com", role=UserRole.ADMIN)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def ta_user(app_ctx):
    from website.models import User

    user = User(first_name="TA", last_name="User", email="ta@x.com", role=UserRole.TA)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def invalid_user(app_ctx):
    from website.models import User

    user = User(first_name="I", last_name="User", email="i@x.com", role=UserRole.INVALID)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def consumable_item(app_ctx, admin_user):
    item = Consumable(name="Test Film", quantity=3, last_updated=datetime.utcnow(), updated_by=admin_user.id)
    db.session.add(item)
    db.session.commit()
    return item


class TestConsumablesEndpoints:
    def test_get_all_consumables_as_admin(self, app, app_ctx, admin_user, consumable_item):
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert "consumables" in data

    def test_create_requires_name_and_ta(self, app, app_ctx, admin_user, ta_user):
        with app.test_client() as client:
            # student/invalid would fail; use TA
            login_user_in_client(client, ta_user)
            rv = client.post(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_CREATE_ROUTE}", json={})
            assert rv.status_code == 400

    def test_create_and_delete_consumable(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            payload = {"name": "New Paper", "quantity": 7}
            rv = client.post(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_CREATE_ROUTE}", json=payload)
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["name"] == "New Paper"

            # now delete
            cid = data["id"]
            rv2 = client.delete(f"{API_PREFIX}{CONSUMABLES_PREFIX}/{cid}")
            # delete route requires TA; logged in as TA so expect success
            assert rv2.status_code == 200

    def test_update_invalid_expires(self, app, app_ctx, ta_user, consumable_item):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CONSUMABLES_PREFIX}/{consumable_item.id}", json={"expires": "not-a-date"})
            assert rv.status_code == 400

    def test_update_create_tags_and_location_not_found_and_clear_expires(self, app, app_ctx, ta_user, consumable_item):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            # Update to add a new tag
            tag_up = f"tag-updated-{uuid.uuid4().hex[:8]}"
            rv = client.put(f"{API_PREFIX}{CONSUMABLES_PREFIX}/{consumable_item.id}", json={"tags": [tag_up]})
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert tag_up in (data.get("tags") or [])
            # tag should exist in DB now
            assert Tag.query.filter_by(name=tag_up).first() is not None

            # Update with non-existent location id should return 400
            rv2 = client.put(f"{API_PREFIX}{CONSUMABLES_PREFIX}/{consumable_item.id}", json={"location_id": 999})
            assert rv2.status_code == 400

            # Set expires to empty string to clear it
            rv3 = client.put(f"{API_PREFIX}{CONSUMABLES_PREFIX}/{consumable_item.id}", json={"expires": ""})
            assert rv3.status_code == 200
            d3 = json.loads(rv3.data)
            assert d3.get("expires") is None

    def test_create_with_existing_tag_and_location_not_found(self, app, app_ctx, ta_user):
        """Create a consumable using an existing tag (avoid transient duplicate inserts).

        The original test created a new Tag at the same time as the Consumable which
        can produce a transient many-to-many duplicate insert in some SQLAlchemy
        configurations. To avoid that fragility we create the Tag up-front, commit,
        then call the create endpoint using that tag name. Then test the
        location-not-found behavior.
        """
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            # create a tag first so it's persisted before the create call
            tag_name = f"pretag-{uuid.uuid4().hex[:8]}"
            t = Tag(name=tag_name)
            db.session.add(t)
            db.session.commit()

            payload = {"name": "Tagged Item", "quantity": 2, "tags": [tag_name]}
            rv = client.post(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_CREATE_ROUTE}", json=payload)
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert tag_name in (data.get("tags") or [])
            # the tag should exist in the DB
            t2 = Tag.query.filter_by(name=tag_name).first()
            assert t2 is not None

            # attempt create with nonexistent location id -> should return 400
            payload = {"name": "Bad Loc", "location_id": 999}
            rv2 = client.post(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_CREATE_ROUTE}", json=payload)
            assert rv2.status_code == 400

    def test_create_invalid_expires_format(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            payload = {"name": "Bad Expire", "expires": "not-a-date"}
            rv = client.post(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_CREATE_ROUTE}", json=payload)
            assert rv.status_code == 400

    def test_create_location_not_found(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            payload = {"name": "LocMissing", "location_id": 99999}
            rv = client.post(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_CREATE_ROUTE}", json=payload)
            assert rv.status_code == 400

    def test_create_with_new_tag_and_associates(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            tag_name = f"cons-{uuid.uuid4().hex[:8]}"
            payload = {"name": "Tagged Cons", "tags": [tag_name], "quantity": 2}
            rv = client.post(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_CREATE_ROUTE}", json=payload)
            assert rv.status_code == 200
            data = json.loads(rv.data)
            c = Consumable.query.get(data["id"])
            assert any(t.name == tag_name for t in c.tags)

    def test_create_with_duplicate_tags_is_deduped(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            tag_name = f"dup-{uuid.uuid4().hex[:8]}"
            payload = {"name": "DupTagCons", "tags": [tag_name, tag_name], "quantity": 1}
            rv = client.post(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_CREATE_ROUTE}", json=payload)
            assert rv.status_code == 200
            data = json.loads(rv.data)
            c = Consumable.query.get(data["id"])
            # tags should be deduplicated
            assert len({t.name for t in c.tags}) == 1

    def test_update_quantity_changes(self, app, app_ctx, ta_user, consumable_item):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CONSUMABLES_PREFIX}/{consumable_item.id}", json={"quantity": 42})
            assert rv.status_code == 200
            fetched = Consumable.query.get(consumable_item.id)
            assert fetched.quantity == 42

    def test_get_nonexistent_consumable_returns_404(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.get(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_GET_ONE_ROUTE}".replace('<int:consumable_id>', '999999'))
            assert rv.status_code == 404

    def test_update_tags_none_keeps_existing(self, app, app_ctx, ta_user):
        # prepare existing tag and attach it to consumable
        t = Tag(name="keep-cons")
        db.session.add(t)
        db.session.commit()
        c = Consumable(name="KeepCons", quantity=1, last_updated=datetime.utcnow(), updated_by=ta_user.id)
        db.session.add(c)
        db.session.commit()
        c.tags = [t]
        db.session.commit()

        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_UPDATE_ROUTE}".replace('<int:consumable_id>', str(c.id)), json={"name": "KeepConsUpdated"})
            assert rv.status_code == 200
            fetched = Consumable.query.get(c.id)
            assert any(tt.name == "keep-cons" for tt in fetched.tags)

    def test_update_tags_empty_clears_tags(self, app, app_ctx, ta_user):
        t = Tag(name="clear-cons")
        db.session.add(t)
        db.session.commit()
        c = Consumable(name="ClearCons", quantity=1, last_updated=datetime.utcnow(), updated_by=ta_user.id)
        db.session.add(c)
        db.session.commit()
        c.tags = [t]
        db.session.commit()

        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_UPDATE_ROUTE}".replace('<int:consumable_id>', str(c.id)), json={"tags": []})
            assert rv.status_code == 200
            fetched = Consumable.query.get(c.id)
            assert fetched.tags == []

    def test_update_clear_location_with_empty_string(self, app, app_ctx, ta_user):
        loc = Location(name="Shelf")
        db.session.add(loc)
        db.session.commit()
        c = Consumable(name="LocClear", quantity=1, last_updated=datetime.utcnow(), updated_by=ta_user.id, location=loc)
        db.session.add(c)
        db.session.commit()

        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CONSUMABLES_PREFIX}{CONSUMABLES_UPDATE_ROUTE}".replace('<int:consumable_id>', str(c.id)), json={"location_id": ""})
            assert rv.status_code == 200
            fetched = Consumable.query.get(c.id)
            assert fetched.location is None
