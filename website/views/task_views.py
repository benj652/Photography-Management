"""Internal task endpoints (invoked by CI schedulers like GitHub Actions).

These endpoints are intentionally small and secured by a shared
secret token (WEEKLY_TASK_TOKEN). Keep the token secret and store it
in GitHub Actions as a repository secret if you trigger the endpoint
from a workflow.
"""

import os

from flask import Blueprint, request, abort, current_app

# Importing the task helpers at module import time can create a cyclic
# import with the utils module (which imports models and app context).
# Import the helpers inside the endpoint function to break that cycle.

tasks_blueprint = Blueprint("internal_tasks", __name__, url_prefix="/internal/tasks")


@tasks_blueprint.route("/weekly-expirations", methods=("POST",))
def weekly_expirations():
    """Run the weekly expirations notification.

    Requires header `X-Task-Token` that matches the environment
    variable `WEEKLY_TASK_TOKEN`.
    """
    token = request.headers.get("X-Task-Token")
    expected = os.getenv("WEEKLY_TASK_TOKEN")
    if not expected or not token or token != expected:
        current_app.logger.warning("Unauthorized attempt to run weekly expirations")
        abort(403)

    # Run the helper synchronously inside the request (app) context.
    try:
        # Import helpers here to avoid cyclic imports at module import time.
        from ..utils import (
            notify_consumables_expiring_this_week,
            notify_camera_gear_due_returns,
            notify_lab_equipment_service_reminders,
        )

        # run all three weekly checks; each helper logs failures individually
        notify_consumables_expiring_this_week()
        notify_camera_gear_due_returns()
        notify_lab_equipment_service_reminders()
    except Exception:
        current_app.logger.exception("Error while running weekly expirations task")
        # return an explicit 500 response so callers and tests can detect it
        return ("Internal Server Error", 500)

    return ("OK", 200)
