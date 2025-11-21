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
    """Send a low-stock alert for `item` to all admin users.

    - `item` is expected to be a SQLAlchemy model instance with at least
      `.id`, `.name`, `.quantity`, and optionally `.location`.
    - `threshold` if provided overrides the environment variable.

    This function is resilient: if mail isn't configured or there are no
    admin recipients it returns silently.
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

    # collect admin recipients
    admins = User.query.filter_by(role=UserRole.ADMIN).all()
    recipients = [u.email for u in admins if getattr(u, "email", None)]
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


def send_expiration_alerts(items: list) -> None:
    """Send an expiration summary email to all admin users for the provided items list.

    `items` is a list of Item model instances. If no recipients or mail
    isn't initialized, this function returns silently.
    """
    global mail

    if not items:
        return

    if mail is None:
        return

    try:
        from models.user import User
        from constants import UserRole
    except Exception:
        return

    admins = User.query.filter_by(role=UserRole.ADMIN).all()
    recipients = [u.email for u in admins if getattr(u, "email", None)]
    if not recipients:
        return

    subject = f"Expiring items in next 7 days ({len(items)})"
    lines = [
        f"The following items are expiring within the next 7 days:",
    ]
    for it in items:
        loc = getattr(it, "location", None)
        loc_name = loc.name if loc else "Unknown"
        expires = it.expires.isoformat() if getattr(it, "expires", None) else "N/A"
        lines.append(f"- {it.name} (id: {it.id}) — expires: {expires} — location: {loc_name} — qty: {getattr(it, 'quantity', 'N/A')}")

    body = "\n".join(lines)

    try:
        msg = EmailMessage(subject=subject, to=recipients, body=body)
        msg.send()
    except Exception:
        if current_app and current_app.logger:
            current_app.logger.exception("Failed to send expiration alert email")
        return
