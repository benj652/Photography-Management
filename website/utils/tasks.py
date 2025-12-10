"""Helpers to send weekly notification emails about consumables,
camera gear returns, and lab equipment service reminders.

These functions are intentionally resilient: they try DB filtering
first and fall back to in-Python filtering if the ORM does not
implement the needed comparisons. They log but do not raise when
sending fails so callers can invoke them from scheduled jobs safely.
"""

from datetime import date, timedelta
from typing import List

from flask_mailman import EmailMessage

from ..models import (
    Consumable,
    User,
    CameraGear,
    LabEquipment
)
from ..constants import UserRole


def notify_consumables_expiring_this_week() -> bool:
    """Find consumables expiring within the next 7 days and email admins/TAs.

    Returns True if an email was sent (or attempted), False if there were
    no expiring items or no recipients.
    """
    today = date.today()
    week_end = today + timedelta(days=6)

    try:
        # Preferred: let the DB filter by date range
        items: List[Consumable] = (
            Consumable.query.filter(
                Consumable.expires is not None,
                Consumable.expires >= today,
                Consumable.expires <= week_end,
            )
            .all()
        )
    except Exception:  # pragma: no cover - fallback path exercised in tests
        # Fallback to in-Python filtering if the DB doesn't support comparisons
        items = [
            c
            for c in Consumable.query.all()
            if c.expires and today <= c.expires <= week_end
        ]

    if not items:
        if current_app and current_app.logger:
            current_app.logger.info(
                "No consumables expiring this week; skipping email."
            )
        return False

    # Collect admin/TA recipients
    try:
        recipients_q = (
            User.query
            .filter(User.role.in_([UserRole.ADMIN, UserRole.TA]))
            .all()
        )
    except Exception:  # pragma: no cover - fallback path exercised in tests
        recipients_q = [u for u in User.query.all() if u.role in (UserRole.ADMIN, UserRole.TA)]

    recipients = [u.email for u in recipients_q if getattr(u, "email", None)]
    if not recipients:
        if current_app and current_app.logger:
            current_app.logger.info("No admin/TA recipients for expiration notifications.")
        return False

    subject = f"Consumables expiring the week of {today.isoformat()}"
    lines: List[str] = ["Consumables expiring this week:", ""]
    for c in items:
        loc = getattr(c, "location", None)
        locname = loc.name if loc else "Unknown"
        expires = c.expires.isoformat() if c.expires else "N/A"
        lines.append(
            f"- {c.name} (id: {c.id}) — expires: {expires} — qty: {c.quantity} "
            f"— location: {locname}"
        )

    body = "\n".join(lines)

    try:
        msg = EmailMessage(subject=subject, to=recipients, body=body)
        msg.send()
    except Exception:  # pragma: no cover - error path exercised in tests
        if current_app and current_app.logger:
            current_app.logger.exception("Failed to send weekly expiration email")

    return True


def send_weekly_expiration_notifications() -> bool:
    """Compatibility wrapper: call the notification helper.

    Keeps the previous name available so callers can run the same function
    when invoked by an endpoint or a worker.
    """
    return notify_consumables_expiring_this_week()


def notify_camera_gear_due_returns(within_days: int = 7) -> bool:  # pylint: disable=too-many-branches,too-many-locals
    """Notify admins/TAs about camera gear that should be returned within
    `within_days` (inclusive) or that are already overdue.

    Returns True if an email was sent (or attempted), False otherwise.
    """
    today = date.today()
    window_end = today + timedelta(days=within_days - 1)

    try:
        items = (
            CameraGear.query.filter(
                CameraGear.is_checked_out is True,
                CameraGear.return_date is not None,
                CameraGear.return_date >= today,
                CameraGear.return_date <= window_end,
            )
            .all()
        )
    except Exception:  # pragma: no cover - fallback exercised in tests
        # fallback to in-Python filtering
        items = [
            g
            for g in CameraGear.query.all()
            if g.is_checked_out and g.return_date and today <= g.return_date <= window_end
        ]

    # include overdue items (return_date < today)
    try:
        overdue = CameraGear.query.filter(
            CameraGear.is_checked_out is True, CameraGear.return_date < today
        ).all()
    except Exception:  # pragma: no cover - fallback exercised in tests
        overdue = [g for g in CameraGear.query.all() if g.is_checked_out and g.return_date and g.return_date < today]

    all_items = items + [o for o in overdue if o not in items]
    if not all_items:
        if current_app and current_app.logger:
            current_app.logger.info("No camera gear due for return this week.")
        return False

    # recipients: admins and TAs
    try:
        recipients_q = User.query.filter(User.role.in_([UserRole.ADMIN, UserRole.TA])).all()
    except Exception:  # pragma: no cover - fallback exercised in tests
        recipients_q = [u for u in User.query.all() if u.role in (UserRole.ADMIN, UserRole.TA)]

    recipients = [u.email for u in recipients_q if getattr(u, "email", None)]
    if not recipients:
        if current_app and current_app.logger:
            current_app.logger.info("No admin/TA recipients for camera gear return notifications.")
        return False

    subject = f"Camera gear return reminders (week of {today.isoformat()})"
    lines = ["Camera gear due for return or overdue:", ""]
    for g in all_items:
        loc = getattr(g, "location", None)
        locname = loc.name if loc else "Unknown"
        return_date = g.return_date.isoformat() if g.return_date else "Unknown"
        checked_out_by = None
        try:
            if getattr(g, "checked_out_by_user", None):
                checked_out_by = g.checked_out_by_user.email
            else:
                checked_out_by = g.checked_out_by
        except Exception:  # pragma: no cover - defensive
            checked_out_by = None
        lines.append(
            f"- {g.name} (id: {g.id}) — return_date: {return_date} — checked_out_by: {checked_out_by} — location: {locname}"
        )

    body = "\n".join(lines)

    try:
        msg = EmailMessage(subject=subject, to=recipients, body=body)
        msg.send()
    except Exception:  # pragma: no cover - error path exercised in tests
        if current_app and current_app.logger:
            current_app.logger.exception("Failed to send camera gear return email")

    return True


def _parse_service_frequency(freq: str) -> int | None:
    """Parse a human-friendly service_frequency into days.

    Accepts common values like 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    or strings like '30', '30 days'. Returns number of days or None if unknown.
    """
    if not freq:
        return None
    f = freq.strip().lower()
    mapping = {
        "daily": 1,
        "weekly": 7,
        "monthly": 30,
        "quarterly": 90,
        "yearly": 365,
        "annually": 365,
    }
    if f in mapping:
        return mapping[f]
    # try to extract number
    try:
        if f.endswith(" days"):
            return int(f.split()[0])
        return int(f)
    except Exception:  # pragma: no cover - parsing failure
        return None


def notify_lab_equipment_service_reminders() -> bool:  # pylint: disable=too-many-branches
    """Notify admins/TAs about lab equipment due for service based on
    `last_serviced_on` + `service_frequency`.

    Returns True if an email was sent (or attempted), False otherwise.
    """
    today = date.today()
    due_items = []

    for eq in LabEquipment.query.all():
        try:
            if not eq.service_frequency or not eq.last_serviced_on:
                continue
            days = _parse_service_frequency(eq.service_frequency)
            if days is None:
                continue
            next_due = eq.last_serviced_on + timedelta(days=days)
            if next_due <= today:
                due_items.append((eq, next_due))
        except Exception:  # pragma: no cover - skip problematic records
            # be conservative and skip problematic records
            continue

    if not due_items:
        if current_app and current_app.logger:
            current_app.logger.info("No lab equipment due for service this week.")
        return False

    # recipients: admins and TAs
    try:
        recipients_q = User.query.filter(User.role.in_([UserRole.ADMIN, UserRole.TA])).all()
    except Exception:  # pragma: no cover - fallback exercised in tests
        recipients_q = [u for u in User.query.all() if u.role in (UserRole.ADMIN, UserRole.TA)]

    recipients = [u.email for u in recipients_q if getattr(u, "email", None)]
    if not recipients:
        if current_app and current_app.logger:
            current_app.logger.info("No admin/TA recipients for lab equipment service notifications.")
        return False

    subject = f"Lab equipment service reminders (as of {today.isoformat()})"
    lines = ["Lab equipment due for service:", ""]
    for eq, due in due_items:
        last_serviced = eq.last_serviced_on.isoformat() if eq.last_serviced_on else "Unknown"
        lines.append(
            f"- {eq.name} (id: {eq.id}) — last_serviced_on: {last_serviced} "
            f"— next_due: {due.isoformat()} — frequency: {eq.service_frequency}"
        )

    body = "\n".join(lines)
    try:
        msg = EmailMessage(subject=subject, to=recipients, body=body)
        msg.send()
    except Exception:  # pragma: no cover - error path exercised in tests
        if current_app and current_app.logger:
            current_app.logger.exception("Failed to send lab equipment service email")

    return True

