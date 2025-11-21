import os
from typing import Optional

from flask import current_app
from flask_mailman import Mail, EmailMessage

# lazy-initialized Mail instance
mail: Optional[Mail] = None


def init_mail(app):
    """Initialize the Mail extension with the given Flask app.
    Call this once from the application factory or main module.
    """
    global mail
    mail = Mail(app)


def send_low_stock_alert(item, threshold: int | None = None) -> None:
    """Send a low-stock alert for `item` to all admin and TA users.

    - `item` is expected to be a SQLAlchemy model instance with at least
      `.id`, `.name`, `.quantity`, and optionally `.location`.
    - `threshold` if provided overrides the environment variable.

    This function is resilient: if mail isn't configured or there are no
    recipients (admins or TAs) it returns silently.
    """
    global mail

    try:
        # Only send if item's quantity is at-or-below configured threshold
        if threshold is None:
            threshold = int(os.getenv("LOW_STOCK_THRESHOLD", "5"))
    except Exception:
        # fallback default
        threshold = 5

    try:
        if item.quantity is None or int(item.quantity) > int(threshold):
            return
    except Exception:
        # if quantity can't be interpreted, don't send
        return

    if mail is None:
        # Mail not initialized; nothing to do
        return

    # Import here to avoid circular imports at app import time
    try:
        from models.user import User
        from constants import UserRole
    except Exception:
        return

    # collect admin and TA recipients
    try:
        recipients_q = User.query.filter(User.role.in_([UserRole.ADMIN, UserRole.TA])).all()
    except Exception:
        # fallback if the database/ORM doesn't support Enum.in_ directly
        recipients_q = [u for u in User.query.all() if u.role in (UserRole.ADMIN, UserRole.TA)]
    recipients = [u.email for u in recipients_q if getattr(u, "email", None)]
    if not recipients:
        return

    subject = f"Low stock alert: {item.name}"
    location_name = getattr(item, "location", None).name if getattr(item, "location", None) else "Unknown"
    body_lines = [
        f"Item '{item.name}' (id: {item.id}) has low stock.",
        f"Quantity remaining: {item.quantity}",
        f"Location: {location_name}",
        "\nPlease restock or re-order as needed.",
    ]
    body = "\n".join(body_lines)

    try:
        msg = EmailMessage(subject=subject, to=recipients, body=body)
        # allow the extension to handle sending (synchronous)
        msg.send()
    except Exception:
        # swallow errors - do not break main request flow
        if current_app and current_app.logger:
            current_app.logger.exception("Failed to send low-stock email")
        return
