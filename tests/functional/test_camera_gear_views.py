# Functional tests for camera gear endpoints
# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,too-many-lines,import-outside-toplevel,unused-argument,redefined-outer-name,line-too-long

import json
from datetime import datetime

import pytest
import uuid

from website.constants import (
    API_PREFIX,
    CAMERA_GEAR_PREFIX,
    CAMERA_GEAR_ALL_ROUTE,
    CAMERA_GEAR_CREATE_ROUTE,
    CAMERA_GEAR_UPDATE_ROUTE,
    CAMERA_GEAR_GET_ONE_ROUTE,
    CAMERA_GEAR_CHECK_OUT_ROUTE,
    CAMERA_GEAR_CHECK_IN_ROUTE,
    CAMERA_GEAR_DELETE_ROUTE,
)
from website import db
from website.models import CameraGear, Tag
from website.models import Location


@pytest.fixture
def admin_user(app_ctx):
    from website.models import User

    user = User(first_name="Admin", last_name="User", email="admin@x.com", role=__import__('website').constants.UserRole.ADMIN)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def ta_user(app_ctx):
    from website.models import User

    user = User(first_name="TA", last_name="User", email="ta@x.com", role=__import__('website').constants.UserRole.TA)
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def student_user(app_ctx):
    from website.models import User

    user = User(first_name="Student", last_name="User", email="s@x.com", role=__import__('website').constants.UserRole.STUDENT)
    db.session.add(user)
    db.session.commit()
    return user



def login_user_in_client(client, user):
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
        sess['_fresh'] = True


@pytest.fixture
def gear_item(app_ctx, admin_user):
    gear = CameraGear(name="Test Lens", last_updated=datetime.utcnow(), updated_by=admin_user.id)
    db.session.add(gear)
    db.session.commit()
    return gear


class TestCameraGearEndpoints:
    def test_get_all_camera_gear_as_admin(self, app, app_ctx, admin_user, gear_item):
        with app.test_client() as client:
            login_user_in_client(client, admin_user)
            rv = client.get(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_ALL_ROUTE}")
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert "camera_gear" in data

    def test_create_requires_name_and_ta(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.post(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_CREATE_ROUTE}", json={})
            assert rv.status_code == 400

    def test_create_and_delete_camera_gear(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            payload = {"name": "New Camera", "tags": []}
            rv = client.post(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_CREATE_ROUTE}", json=payload)
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["name"] == "New Camera"

            gid = data["id"]
            rv2 = client.delete(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}/{gid}")
            assert rv2.status_code == 200

    def test_update_location_not_found(self, app, app_ctx, ta_user, gear_item):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_UPDATE_ROUTE}".replace('<int:gear_id>', str(gear_item.id)), json={"location_id": 999})
            # update returns 404 when location not found
            assert rv.status_code == 404

    def test_checkout_and_checkin_flow(self, app, app_ctx, ta_user, gear_item):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            # checkout
            rv = client.put(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_CHECK_OUT_ROUTE}".replace('<int:gear_id>', str(gear_item.id)))
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data.get("is_checked_out") is True

            # second checkout should fail
            rv2 = client.put(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_CHECK_OUT_ROUTE}".replace('<int:gear_id>', str(gear_item.id)))
            assert rv2.status_code == 400

            # checkin
            rv3 = client.put(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_CHECK_IN_ROUTE}".replace('<int:gear_id>', str(gear_item.id)))
            assert rv3.status_code == 200
            d3 = json.loads(rv3.data)
            assert d3.get("is_checked_out") is False

            # second checkin should fail
            rv4 = client.put(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_CHECK_IN_ROUTE}".replace('<int:gear_id>', str(gear_item.id)))
            assert rv4.status_code == 400

    def test_create_with_new_tag_and_associates(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            tag_name = f"tag-{uuid.uuid4().hex[:8]}"
            payload = {"name": "New Camera Tagged", "tags": [tag_name]}
            rv = client.post(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_CREATE_ROUTE}", json=payload)
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["name"] == "New Camera Tagged"
            # verify tag exists
            t = Tag.query.filter_by(name=tag_name).first()
            assert t is not None
            gear = CameraGear.query.get(data["id"])
            assert any(tt.name == tag_name for tt in gear.tags)

    def test_update_tags_none_keeps_existing(self, app, app_ctx, ta_user):
        # prepare gear with a tag
        t = Tag(name="keep-tag")
        db.session.add(t)
        db.session.commit()
        # create gear first, then assign tags to avoid transient many-to-many duplicate inserts
        gear = CameraGear(name="KeepTags", last_updated=datetime.utcnow(), updated_by=ta_user.id)
        db.session.add(gear)
        db.session.commit()
        gear.tags = [t]
        db.session.commit()

        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_UPDATE_ROUTE}".replace('<int:gear_id>', str(gear.id)), json={"name": "KeepTagsUpdated"})
            assert rv.status_code == 200
            g = CameraGear.query.get(gear.id)
            assert any(tag.name == "keep-tag" for tag in g.tags)

    def test_update_tags_empty_clears_tags(self, app, app_ctx, ta_user):
        t = Tag(name="clear-tag")
        db.session.add(t)
        db.session.commit()
        # create gear first, then assign tags to avoid transient many-to-many duplicate inserts
        gear = CameraGear(name="ClearTags", last_updated=datetime.utcnow(), updated_by=ta_user.id)
        db.session.add(gear)
        db.session.commit()
        gear.tags = [t]
        db.session.commit()

        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_UPDATE_ROUTE}".replace('<int:gear_id>', str(gear.id)), json={"tags": []})
            assert rv.status_code == 200
            g = CameraGear.query.get(gear.id)
            assert g.tags == []

    def test_update_clear_location_with_empty_string(self, app, app_ctx, ta_user):
        loc = Location(name="Shelf")
        db.session.add(loc)
        db.session.commit()
        gear = CameraGear(name="LocGear", last_updated=datetime.utcnow(), updated_by=ta_user.id, location_id=loc.id)
        db.session.add(gear)
        db.session.commit()

        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_UPDATE_ROUTE}".replace('<int:gear_id>', str(gear.id)), json={"location_id": ""})
            assert rv.status_code == 200
            g = CameraGear.query.get(gear.id)
            assert g.location_id is None

    def test_get_one_camera_gear_as_ta(self, app, app_ctx, ta_user):
        gear = CameraGear(name="SingleGet", last_updated=datetime.utcnow(), updated_by=ta_user.id)
        db.session.add(gear)
        db.session.commit()

        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.get(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_GET_ONE_ROUTE}".replace('<int:gear_id>', str(gear.id)))
            assert rv.status_code == 200
            data = json.loads(rv.data)
            assert data["id"] == gear.id

    def test_create_with_existing_tag(self, app, app_ctx, ta_user):
        # pre-create tag then create gear using that tag name
        tname = f"pre-{uuid.uuid4().hex[:8]}"
        t = Tag(name=tname)
        db.session.add(t)
        db.session.commit()

        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            payload = {"name": "UsingPreTag", "tags": [tname]}
            rv = client.post(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_CREATE_ROUTE}", json=payload)
            assert rv.status_code == 200
            data = json.loads(rv.data)
            gear = CameraGear.query.get(data["id"])
            assert any(tt.name == tname for tt in gear.tags)

    def test_update_set_location_success(self, app, app_ctx, ta_user, gear_item):
        loc = Location(name="Shelf")
        db.session.add(loc)
        db.session.commit()

        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.put(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_UPDATE_ROUTE}".replace('<int:gear_id>', str(gear_item.id)), json={"location_id": loc.id})
            assert rv.status_code == 200
            g = CameraGear.query.get(gear_item.id)
            assert g.location_id == loc.id

    def test_delete_nonexistent_returns_404(self, app, app_ctx, ta_user):
        with app.test_client() as client:
            login_user_in_client(client, ta_user)
            rv = client.delete(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}/999999")
            assert rv.status_code == 404

    def test_get_one_forbidden_for_student(self, app, app_ctx, student_user, gear_item):
        with app.test_client() as client:
            login_user_in_client(client, student_user)
            rv = client.get(f"{API_PREFIX}{CAMERA_GEAR_PREFIX}{CAMERA_GEAR_GET_ONE_ROUTE}".replace('<int:gear_id>', str(gear_item.id)))
            assert rv.status_code == 403
