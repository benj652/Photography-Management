"""Mail helpers and small email utilities.

Provides a thin wrapper around the Flask-Mailman extension. Functions
are resilient when mail isn't configured so they won't break request
flows if sending fails.
"""

import os
from typing import Optional

from flask import Flask, current_app
from flask_mailman import Mail, EmailMessage

# lazy-initialized Mail instance
mail: Optional[Mail] = None


def init_mail(app: Flask) -> None:
    """Initialize the Mail extension with the given Flask app.

    Call this once from the application factory or main module.
    """
    global mail
    mail = Mail(app)


def send_low_stock_alert(item, threshold: int | None = None) -> bool:
    """Send a low-stock alert for `item` to all admin and TA users.

    Returns True if an email was sent (or attempted), False if no email
    was necessary (quantity above threshold) or there were no recipients.

    Behavior is resilient and mirrors the notification helpers in
    `website.utils.tasks`: try DB operations first, fall back to in-Python
    logic, log failures, and do not raise from this helper.
    """
    # Determine threshold (env override)
    try:
        if threshold is None:
            threshold = int(os.getenv("LOW_STOCK_THRESHOLD", "5"))
    except Exception:  # pragma: no cover - defensive
        threshold = 5

    # Only proceed if item quantity is at-or-below threshold
    try:
        if item.quantity is None or int(item.quantity) > int(threshold):
            if current_app and current_app.logger:
                current_app.logger.info(
                    "Item %s (id:%s) above low-stock threshold; skipping.",
                    getattr(item, "name", "?"),
                    getattr(item, "id", "?"),
                )
            return False
    except (TypeError, ValueError):  # pragma: no cover - defensive
        # if quantity can't be interpreted, do not send
        if current_app and current_app.logger:
            current_app.logger.info(
                "Could not interpret quantity for item %s; skipping low-stock alert.",
                getattr(item, "id", "?"),
            )
        return False

    # If Mail isn't initialized, nothing to do.
    if mail is None:
        if current_app and current_app.logger:
            current_app.logger.info("Mail extension not initialized; skipping low-stock alert for item id %s", getattr(item, "id", "?"))
        return False

    # Import here to avoid circular imports at app import time
    try:
        from ..models import User  # local import to avoid cycles
        from ..constants import UserRole
    except (ImportError, ModuleNotFoundError):  # pragma: no cover - defensive
        if current_app and current_app.logger:
            current_app.logger.exception(
                "Failed to import User/roles for low-stock alert",
            )
        return False

    # collect admin and TA recipients
    try:
        recipients_q = (
            User.query.filter(
                User.role.in_([UserRole.ADMIN, UserRole.TA])
            ).all()
        )
    except Exception:  # pragma: no cover - fallback exercised in tests
        recipients_q = [
            u for u in User.query.all() if u.role in (UserRole.ADMIN, UserRole.TA)
        ]

    recipients = [u.email for u in recipients_q if getattr(u, "email", None)]
    if not recipients:
        if current_app and current_app.logger:
            current_app.logger.info("No admin/TA recipients for low-stock alert for item id %s", getattr(item, "id", "?"))
        return False

    subject = f"Low stock alert: {item.name}"
    location = getattr(item, "location", None)
    location_name = location.name if location else "Unknown"
    body_lines = [
        f"Item '{item.name}' (id: {item.id}) has low stock.",
        f"Quantity remaining: {item.quantity}",
        f"Location: {location_name}",
        "\nPlease restock or re-order as needed.",
    ]
    body = "\n".join(body_lines)

    try:
        msg = EmailMessage(subject=subject, to=recipients, body=body)
        msg.send()
    except Exception:  # pragma: no cover - error path exercised in tests
        if current_app and current_app.logger:
            current_app.logger.exception(
                "Failed to send low-stock email for item id %s",
                getattr(item, "id", "?"),
            )
        # we attempted to send but it failed; return True to indicate an attempt
        return True

    return True
