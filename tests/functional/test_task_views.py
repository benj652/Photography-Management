"""Tests for the internal tasks endpoint.

These are functional unit tests that run in-process. Linting for
tests is relaxed because tests intentionally patch modules and use
fixtures in ways pylint cannot always infer.
"""

# pylint: disable=missing-module-docstring,import-error,line-too-long,
# pylint: disable=missing-function-docstring,missing-class-docstring,unused-import
import os

import website.views.task_views as view_module


def test_weekly_endpoint_unauthorized(app):
    client = app.test_client()
    # Ensure token not present in environment for this unauthorized test
    os.environ.pop("WEEKLY_TASK_TOKEN", None)
    rv = client.post("/internal/tasks/weekly-expirations")
    assert rv.status_code == 403


def test_weekly_endpoint_success(app, patcher):
    # patch helpers to no-op and ensure endpoint returns 200
    def ok1():
        return True

    # The view lazily imports helpers from `website.utils.tasks` at runtime;
    # patch the functions on that module so the endpoint runs the patched
    # versions when invoked.
    import website.utils as utils_pkg
    patcher(utils_pkg, "notify_consumables_expiring_this_week", ok1)
    patcher(utils_pkg, "notify_camera_gear_due_returns", ok1)
    patcher(utils_pkg, "notify_lab_equipment_service_reminders", ok1)

    client = app.test_client()
    # set a matching token in environment and header
    token = "test-token-xyz"
    os.environ["WEEKLY_TASK_TOKEN"] = token

    rv = client.post("/internal/tasks/weekly-expirations", headers={"X-Task-Token": token})
    assert rv.status_code == 200


def test_weekly_endpoint_internal_error(app, patcher):
    # patch one helper to raise to force 500
    def bad():
        raise RuntimeError("boom")

    import website.utils as utils_pkg
    patcher(utils_pkg, "notify_consumables_expiring_this_week", bad)
    patcher(utils_pkg, "notify_camera_gear_due_returns", lambda: True)
    patcher(utils_pkg, "notify_lab_equipment_service_reminders", lambda: True)

    token = "test-token-xyz-2"
    os.environ["WEEKLY_TASK_TOKEN"] = token

    client = app.test_client()
    rv = client.post("/internal/tasks/weekly-expirations", headers={"X-Task-Token": token})
    assert rv.status_code == 500
