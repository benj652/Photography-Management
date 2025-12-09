import types

import pytest

from app import app as flask_app
import utils.tasks as tasks
import views.task_views as view_module


def test_weekly_endpoint_unauthorized(app):
    client = app.test_client()
    # Ensure token not present in environment for this unauthorized test
    import os
    os.environ.pop("WEEKLY_TASK_TOKEN", None)
    rv = client.post("/internal/tasks/weekly-expirations")
    assert rv.status_code == 403


def test_weekly_endpoint_success(app, patcher):
    # patch helpers to no-op and ensure endpoint returns 200
    def ok1():
        return True

    # patch the functions in the views module because the view imported
    # them at module import time
    patcher(view_module, "notify_consumables_expiring_this_week", ok1)
    patcher(view_module, "notify_camera_gear_due_returns", ok1)
    patcher(view_module, "notify_lab_equipment_service_reminders", ok1)

    client = app.test_client()
    # set a matching token in environment and header
    import os
    token = "test-token-xyz"
    os.environ["WEEKLY_TASK_TOKEN"] = token

    rv = client.post("/internal/tasks/weekly-expirations", headers={"X-Task-Token": token})
    assert rv.status_code == 200


def test_weekly_endpoint_internal_error(app, patcher):
    # patch one helper to raise to force 500
    def bad():
        raise RuntimeError("boom")

    patcher(view_module, "notify_consumables_expiring_this_week", bad)
    patcher(view_module, "notify_camera_gear_due_returns", lambda: True)
    patcher(view_module, "notify_lab_equipment_service_reminders", lambda: True)

    import os
    token = "test-token-xyz-2"
    os.environ["WEEKLY_TASK_TOKEN"] = token

    client = app.test_client()
    rv = client.post("/internal/tasks/weekly-expirations", headers={"X-Task-Token": token})
    assert rv.status_code == 500
