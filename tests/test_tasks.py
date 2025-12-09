"""Unit tests for the notification helpers in `utils.tasks`.

The test module intentionally uses dynamic patching and a number of
test-only patterns that pylint will flag; we relax linting for this
file to keep tests readable and focused on behavior.
"""

# pylint: disable=missing-module-docstring,too-many-lines,line-too-long,
# pylint: disable=import-error,missing-function-docstring,missing-class-docstring,
# pylint: disable=too-few-public-methods,unused-argument,consider-using-from-import,
# pylint: disable=broad-exception-caught,import-outside-toplevel,protected-access,
# pylint: disable=multiple-statements,redefined-outer-name,broad-exception-raised,
# pylint: disable=unused-import

from datetime import date, timedelta
import types

import pytest

import utils.tasks as tasks


def make_fake_query(items=None, raise_on_filter=False):
    class FakeQuery:
        def __init__(self, items=None, _raise=False):
            self._items = items or []
            self._raise = _raise

        def filter(self, *args, **kwargs):
            if self._raise:
                raise Exception("db filter error")
            return self

        def all(self):
            return list(self._items)

    return FakeQuery(items, raise_on_filter)


def test_notify_consumables_no_items(app_ctx, patcher):
    fake_consumable = types.SimpleNamespace()
    fake_consumable.query = make_fake_query([])
    patcher(tasks, "Consumable", fake_consumable)

    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([])
    patcher(tasks, "User", fake_user)

    assert tasks.notify_consumables_expiring_this_week() is False


def test_notify_consumables_with_items_and_recipients(app_ctx, patcher):
    c = types.SimpleNamespace(id=1, name="Film A", quantity=2, location=types.SimpleNamespace(name="Shelf"), expires=date.today())
    fake_consumable = types.SimpleNamespace()
    fake_consumable.query = make_fake_query([c])
    patcher(tasks, "Consumable", fake_consumable)

    u = types.SimpleNamespace(email="admin@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    sent = {}

    class FakeEM:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = to
            sent['body'] = body

        def send(self):
            sent['sent'] = True

    patcher(tasks, "EmailMessage", FakeEM)

    assert tasks.notify_consumables_expiring_this_week() is True
    assert sent.get('sent') is True
    assert "Film A" in sent.get('body', "")


def test_notify_consumables_email_failure_logs(app_ctx, patcher):
    c = types.SimpleNamespace(id=2, name="Paper", quantity=1, location=types.SimpleNamespace(name="Cabinet"), expires=date.today())
    fake_consumable = types.SimpleNamespace()
    fake_consumable.query = make_fake_query([c])
    patcher(tasks, "Consumable", fake_consumable)

    u = types.SimpleNamespace(email="admin2@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    class FakeEMBad:
        def __init__(self, subject=None, to=None, body=None):
            pass

        def send(self):
            raise RuntimeError("smtp down")

    patcher(tasks, "EmailMessage", FakeEMBad)

    logged = {}

    def fake_exc(*a, **k):
        logged['exc'] = True

    # attach logger.exception
    from app import app as flask_app
    orig_exc = flask_app.logger.exception
    flask_app.logger.exception = fake_exc

    try:
        assert tasks.notify_consumables_expiring_this_week() is True
        assert logged.get('exc')
    finally:
        flask_app.logger.exception = orig_exc


def test_parse_service_frequency():
    assert tasks._parse_service_frequency("daily") == 1
    assert tasks._parse_service_frequency("30") == 30
    assert tasks._parse_service_frequency("30 days") == 30
    assert tasks._parse_service_frequency("unknown") is None


def test_notify_camera_gear_due_returns(app_ctx, patcher):
    today = date.today()
    g1 = types.SimpleNamespace(id=10, name="Lens", is_checked_out=True, return_date=today + timedelta(days=2), location=types.SimpleNamespace(name="Locker"), checked_out_by=5, checked_out_by_user=None)
    g2 = types.SimpleNamespace(id=11, name="Tripod", is_checked_out=True, return_date=today - timedelta(days=1), location=None, checked_out_by=None, checked_out_by_user=types.SimpleNamespace(email="user@example.com"))

    fake_camera = types.SimpleNamespace()
    # We'll have two sequential filter calls: first returns [g1], second returns [g2] for overdue
    class ToggleQuery:
        def __init__(self, first, second):
            self.calls = 0
            self.first = first
            self.second = second

        def filter(self, *a, **k):
            self.calls += 1
            return self

        def all(self):
            return self.first if self.calls == 1 else self.second

    fake_camera.query = ToggleQuery([g1], [g2])
    patcher(tasks, "CameraGear", fake_camera)

    u = types.SimpleNamespace(email="admin3@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    sent = {}

    class FakeEM:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = to
            sent['body'] = body

        def send(self):
            sent['sent'] = True

    patcher(tasks, "EmailMessage", FakeEM)

    assert tasks.notify_camera_gear_due_returns() is True
    assert sent.get('sent') is True


def test_notify_lab_equipment_service_reminders(app_ctx, patcher):
    today = date.today()
    eq1 = types.SimpleNamespace(id=20, name="Printer", last_serviced_on=today - timedelta(days=40), service_frequency="30")
    eq2 = types.SimpleNamespace(id=21, name="Scanner", last_serviced_on=today - timedelta(days=10), service_frequency="monthly")

    fake_lab = types.SimpleNamespace()
    fake_lab.query = make_fake_query([eq1, eq2])
    patcher(tasks, "LabEquipment", fake_lab)

    u = types.SimpleNamespace(email="admin4@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    sent = {}

    class FakeEM:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = to
            sent['body'] = body

        def send(self):
            sent['sent'] = True

    patcher(tasks, "EmailMessage", FakeEM)

    assert tasks.notify_lab_equipment_service_reminders() is True
    assert sent.get('sent') is True


def test_notify_camera_gear_filter_raises_and_overdue_fallback(app_ctx, patcher):
    # Simulate .filter() raising so functions use the .all() fallback to locate items
    today = date.today()
    g_overdue = types.SimpleNamespace(id=40, name="OldFlash", is_checked_out=True, return_date=today - timedelta(days=2), location=None, checked_out_by=None, checked_out_by_user=types.SimpleNamespace(email="late@example.com"))
    g_upcoming = types.SimpleNamespace(id=41, name="NewFlash", is_checked_out=True, return_date=today + timedelta(days=3), location=types.SimpleNamespace(name="Room"), checked_out_by=9, checked_out_by_user=None)

    fake_camera = types.SimpleNamespace()
    # make filter raise; .all() will return both items so the fallback code picks them up
    fake_camera.query = make_fake_query([g_overdue, g_upcoming], raise_on_filter=True)
    patcher(tasks, "CameraGear", fake_camera)

    u = types.SimpleNamespace(email="admin5@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u], raise_on_filter=True)
    patcher(tasks, "User", fake_user)

    sent = {}

    class FakeEM:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = to
            sent['body'] = body

        def send(self):
            sent['sent'] = True

    patcher(tasks, "EmailMessage", FakeEM)

    assert tasks.notify_camera_gear_due_returns() is True
    assert sent.get('sent') is True


def test_notify_camera_gear_no_recipients_returns_false(app_ctx, patcher):
    today = date.today()
    g = types.SimpleNamespace(id=50, name="Strap", is_checked_out=True, return_date=today + timedelta(days=1), location=None, checked_out_by=None, checked_out_by_user=None)

    fake_camera = types.SimpleNamespace()
    fake_camera.query = make_fake_query([g])
    patcher(tasks, "CameraGear", fake_camera)

    # users exist but have no emails
    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    assert tasks.notify_camera_gear_due_returns() is False


def test_parse_service_frequency_more_values():
    assert tasks._parse_service_frequency("monthly") == 30
    assert tasks._parse_service_frequency("quarterly") == 90
    assert tasks._parse_service_frequency("annually") == 365


def test_lab_equipment_recipient_filter_raises_and_send_exception_logged(app_ctx, patcher):
    today = date.today()
    eq = types.SimpleNamespace(id=60, name="Calibrator", last_serviced_on=today - timedelta(days=400), service_frequency="365")

    fake_lab = types.SimpleNamespace()
    fake_lab.query = make_fake_query([eq])
    patcher(tasks, "LabEquipment", fake_lab)

    # recipients filter raises, fallback to .all() should work
    u = types.SimpleNamespace(email="admin6@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u], raise_on_filter=True)
    patcher(tasks, "User", fake_user)

    class BadEM:
        def __init__(self, subject=None, to=None, body=None):
            pass

        def send(self):
            raise RuntimeError("smtp lab")

    patcher(tasks, "EmailMessage", BadEM)

    # attach logger.exception
    from app import app as flask_app
    orig_exc = flask_app.logger.exception
    logged = {}
    flask_app.logger.exception = lambda *a, **k: logged.setdefault('exc', True)

    try:
        assert tasks.notify_lab_equipment_service_reminders() is True
        assert logged.get('exc')
    finally:
        flask_app.logger.exception = orig_exc


def test_notify_consumable_item_without_location_and_no_email(app_ctx, patcher):
    # item with no location should not crash when formatting body
    c = types.SimpleNamespace(id=70, name="Marker", quantity=10, location=None, expires=date.today())
    fake_consumable = types.SimpleNamespace()
    fake_consumable.query = make_fake_query([c])
    patcher(tasks, "Consumable", fake_consumable)

    # recipients exist but email None -> function returns False
    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    assert tasks.notify_consumables_expiring_this_week() is False


def test_camera_checked_out_by_user_attribute_error(app_ctx, patcher):
    # simulate attribute access raising inside checked_out_by_user
    today = date.today()

    class BadCheckedOut:
        id = 80
        name = "WeirdCam"
        is_checked_out = True
        return_date = today + timedelta(days=2)
        location = None

        @property
        def checked_out_by_user(self):
            raise RuntimeError("boom attr")

        checked_out_by = 123

    fake_camera = types.SimpleNamespace()
    fake_camera.query = make_fake_query([BadCheckedOut()])
    patcher(tasks, "CameraGear", fake_camera)

    u = types.SimpleNamespace(email="admin7@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    sent = {}

    class FakeEM:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = to
            sent['body'] = body

        def send(self):
            sent['sent'] = True

    patcher(tasks, "EmailMessage", FakeEM)

    assert tasks.notify_camera_gear_due_returns() is True
    assert sent.get('sent') is True


def test_all_items_duplicates_filtered_out(app_ctx, patcher):
    # ensure the 'if o not in items' branch is exercised when overdue contains duplicates
    today = date.today()
    g = types.SimpleNamespace(id=90, name="Mono", is_checked_out=True, return_date=today + timedelta(days=1), location=None, checked_out_by=None, checked_out_by_user=None)

    class SameQuery:
        def __init__(self, items):
            self._items = items

        def filter(self, *a, **k):
            return self

        def all(self):
            return list(self._items)

    fake_camera = types.SimpleNamespace()
    # both filter calls will return the same list
    fake_camera.query = SameQuery([g])
    patcher(tasks, "CameraGear", fake_camera)

    u = types.SimpleNamespace(email="admin8@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    sent = {}

    class FakeEM:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = to
            sent['body'] = body

        def send(self):
            sent['sent'] = True

    patcher(tasks, "EmailMessage", FakeEM)

    assert tasks.notify_camera_gear_due_returns() is True
    assert sent.get('sent') is True


def test_current_app_none_logging_skipped(app_ctx, patcher):
    # set current_app to None to exercise branches that check for presence
    orig_app = tasks.current_app
    tasks.current_app = None
    try:
        # consumables: no items
        fake_consumable = types.SimpleNamespace()
        fake_consumable.query = make_fake_query([])
        patcher(tasks, "Consumable", fake_consumable)

        fake_user = types.SimpleNamespace()
        fake_user.query = make_fake_query([])
        patcher(tasks, "User", fake_user)

        assert tasks.notify_consumables_expiring_this_week() is False

        # camera gear: no items
        fake_camera = types.SimpleNamespace()
        fake_camera.query = make_fake_query([])
        patcher(tasks, "CameraGear", fake_camera)

        assert tasks.notify_camera_gear_due_returns() is False

        # lab equipment: no items
        fake_lab = types.SimpleNamespace()
        fake_lab.query = make_fake_query([])
        patcher(tasks, "LabEquipment", fake_lab)

        assert tasks.notify_lab_equipment_service_reminders() is False
    finally:
        tasks.current_app = orig_app


def _make_fake_app_logger():
    logged = {}

    class FakeLogger:
        def info(self, *a, **k):
            logged['info'] = True

        def exception(self, *a, **k):
            logged['exc'] = True

    class FakeApp:
        def __init__(self):
            self.logger = FakeLogger()

    return FakeApp(), logged


def test_consumables_items_empty_logs_info(app_ctx, patcher):
    fake_consumable = types.SimpleNamespace()
    fake_consumable.query = make_fake_query([])
    patcher(tasks, "Consumable", fake_consumable)

    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([])
    patcher(tasks, "User", fake_user)

    fake_app, logged = _make_fake_app_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        assert tasks.notify_consumables_expiring_this_week() is False
        assert logged.get('info')
    finally:
        tasks.current_app = orig_app


def test_consumables_recipients_empty_logs_info(app_ctx, patcher):
    c = types.SimpleNamespace(id=101, name="GlueStick", quantity=1, location=None, expires=date.today())
    fake_consumable = types.SimpleNamespace()
    fake_consumable.query = make_fake_query([c])
    patcher(tasks, "Consumable", fake_consumable)

    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    fake_app, logged = _make_fake_app_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        assert tasks.notify_consumables_expiring_this_week() is False
        assert logged.get('info')
    finally:
        tasks.current_app = orig_app


def test_consumables_email_exception_logs_exception(app_ctx, patcher):
    c = types.SimpleNamespace(id=102, name="Tape2", quantity=1, location=None, expires=date.today())
    fake_consumable = types.SimpleNamespace()
    fake_consumable.query = make_fake_query([c])
    patcher(tasks, "Consumable", fake_consumable)

    u = types.SimpleNamespace(email="admin9@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    class BadEM:
        def __init__(self, subject=None, to=None, body=None):
            pass

        def send(self):
            raise RuntimeError("smtp consumables")

    patcher(tasks, "EmailMessage", BadEM)

    fake_app, logged = _make_fake_app_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        assert tasks.notify_consumables_expiring_this_week() is True
        assert logged.get('exc')
    finally:
        tasks.current_app = orig_app


def test_camera_no_all_items_logs_info(app_ctx, patcher):
    fake_camera = types.SimpleNamespace()
    fake_camera.query = make_fake_query([])
    patcher(tasks, "CameraGear", fake_camera)

    fake_app, logged = _make_fake_app_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        assert tasks.notify_camera_gear_due_returns() is False
        assert logged.get('info')
    finally:
        tasks.current_app = orig_app


def test_camera_recipients_empty_logs_info(app_ctx, patcher):
    today = date.today()
    g = types.SimpleNamespace(id=110, name="Bag", is_checked_out=True, return_date=today + timedelta(days=1), location=None, checked_out_by=None, checked_out_by_user=None)
    fake_camera = types.SimpleNamespace()
    fake_camera.query = make_fake_query([g])
    patcher(tasks, "CameraGear", fake_camera)

    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    fake_app, logged = _make_fake_app_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        assert tasks.notify_camera_gear_due_returns() is False
        assert logged.get('info')
    finally:
        tasks.current_app = orig_app


def test_camera_email_exception_logs_exception(app_ctx, patcher):
    today = date.today()
    g = types.SimpleNamespace(id=120, name="Light", is_checked_out=True, return_date=today + timedelta(days=1), location=None, checked_out_by=None, checked_out_by_user=None)
    fake_camera = types.SimpleNamespace()
    fake_camera.query = make_fake_query([g])
    patcher(tasks, "CameraGear", fake_camera)

    u = types.SimpleNamespace(email="admin10@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    class BadEM2:
        def __init__(self, subject=None, to=None, body=None):
            pass

        def send(self):
            raise RuntimeError("smtp camera")

    patcher(tasks, "EmailMessage", BadEM2)

    fake_app, logged = _make_fake_app_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        assert tasks.notify_camera_gear_due_returns() is True
        assert logged.get('exc')
    finally:
        tasks.current_app = orig_app


def test_parse_service_frequency_empty_and_none():
    assert tasks._parse_service_frequency("") is None
    assert tasks._parse_service_frequency(None) is None


def test_lab_equipment_skip_and_logs_info(app_ctx, patcher):
    # eqs that should be skipped by the loop
    eq1 = types.SimpleNamespace(id=130, name="E1", last_serviced_on=None, service_frequency="30")
    eq2 = types.SimpleNamespace(id=131, name="E2", last_serviced_on=date.today(), service_frequency=None)
    eq3 = types.SimpleNamespace(id=132, name="E3", last_serviced_on=date.today(), service_frequency="unknown")

    fake_lab = types.SimpleNamespace()
    fake_lab.query = make_fake_query([eq1, eq2, eq3])
    patcher(tasks, "LabEquipment", fake_lab)

    fake_app, logged = _make_fake_app_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        assert tasks.notify_lab_equipment_service_reminders() is False
        assert logged.get('info')
    finally:
        tasks.current_app = orig_app


def test_lab_recipients_empty_logs_info(app_ctx, patcher):
    # one due item but recipients have no emails
    eq = types.SimpleNamespace(id=140, name="Pump", last_serviced_on=date.today() - timedelta(days=400), service_frequency="365")
    fake_lab = types.SimpleNamespace()
    fake_lab.query = make_fake_query([eq])
    patcher(tasks, "LabEquipment", fake_lab)

    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    fake_app, logged = _make_fake_app_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        assert tasks.notify_lab_equipment_service_reminders() is False
        assert logged.get('info')
    finally:
        tasks.current_app = orig_app


def test_lab_email_exception_logs_exception(app_ctx, patcher):
    eq = types.SimpleNamespace(id=150, name="Heater", last_serviced_on=date.today() - timedelta(days=400), service_frequency="365")
    fake_lab = types.SimpleNamespace()
    fake_lab.query = make_fake_query([eq])
    patcher(tasks, "LabEquipment", fake_lab)

    u = types.SimpleNamespace(email="admin11@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    class BadEM3:
        def __init__(self, subject=None, to=None, body=None):
            pass

        def send(self):
            raise RuntimeError("smtp lab2")

    patcher(tasks, "EmailMessage", BadEM3)

    fake_app, logged = _make_fake_app_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        assert tasks.notify_lab_equipment_service_reminders() is True
        assert logged.get('exc')
    finally:
        tasks.current_app = orig_app


def test_send_weekly_wrapper_calls_underlying(app_ctx, patcher):
    # ensure the compatibility wrapper forwards to the main function
    called = {}

    def fake_main():
        called['ok'] = True
        return True

    patcher(tasks, 'notify_consumables_expiring_this_week', fake_main)
    assert tasks.send_weekly_expiration_notifications() is True
    assert called.get('ok')


def _app_with_no_logger():
    class AppNoLogger:
        def __init__(self):
            self.logger = None

    return AppNoLogger()


def _app_with_logger():
    class AppWithLogger:
        def __init__(self):
            self.logger = type('L', (), {})()

    app = AppWithLogger()
    # attach methods dynamically so each test can inspect by replacing
    logged = {}

    def info(*a, **k):
        logged['info'] = True

    def exception(*a, **k):
        logged['exc'] = True

    app.logger.info = info
    app.logger.exception = exception
    return app, logged


def test_consumables_recipients_logging_variants(app_ctx, patcher):
    # Prepare an item and a user with no email to force 'no recipients' path
    c = types.SimpleNamespace(id=201, name='C', quantity=1, location=None, expires=date.today())
    fake_consumable = types.SimpleNamespace(); fake_consumable.query = make_fake_query([c])
    patcher(tasks, 'Consumable', fake_consumable)

    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace(); fake_user.query = make_fake_query([u])
    patcher(tasks, 'User', fake_user)

    orig_app = tasks.current_app
    try:
        # None variant
        tasks.current_app = None
        assert tasks.notify_consumables_expiring_this_week() is False

        # app with no logger
        tasks.current_app = _app_with_no_logger()
        assert tasks.notify_consumables_expiring_this_week() is False

        # app with logger
        app, logged = _app_with_logger()
        tasks.current_app = app
        assert tasks.notify_consumables_expiring_this_week() is False
        assert logged.get('info')
    finally:
        tasks.current_app = orig_app


def test_camera_recipients_logging_variants(app_ctx, patcher):
    today = date.today()
    g = types.SimpleNamespace(id=210, name='G', is_checked_out=True, return_date=today + timedelta(days=1), location=None, checked_out_by=None, checked_out_by_user=None)
    fake_camera = types.SimpleNamespace(); fake_camera.query = make_fake_query([g])
    patcher(tasks, 'CameraGear', fake_camera)

    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace(); fake_user.query = make_fake_query([u])
    patcher(tasks, 'User', fake_user)

    orig_app = tasks.current_app
    try:
        tasks.current_app = None
        assert tasks.notify_camera_gear_due_returns() is False

        tasks.current_app = _app_with_no_logger()
        assert tasks.notify_camera_gear_due_returns() is False

        app, logged = _app_with_logger()
        tasks.current_app = app
        assert tasks.notify_camera_gear_due_returns() is False
        assert logged.get('info')
    finally:
        tasks.current_app = orig_app


def test_camera_email_exception_logging_variants(app_ctx, patcher):
    today = date.today()
    g = types.SimpleNamespace(id=220, name='G2', is_checked_out=True, return_date=today + timedelta(days=1), location=None, checked_out_by=None, checked_out_by_user=None)
    fake_camera = types.SimpleNamespace(); fake_camera.query = make_fake_query([g])
    patcher(tasks, 'CameraGear', fake_camera)

    u = types.SimpleNamespace(email='rec@example.com', role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace(); fake_user.query = make_fake_query([u])
    patcher(tasks, 'User', fake_user)

    class BadEM:
        def __init__(self, subject=None, to=None, body=None):
            pass
        def send(self):
            raise RuntimeError('boom')

    patcher(tasks, 'EmailMessage', BadEM)

    orig_app = tasks.current_app
    try:
        tasks.current_app = None
        assert tasks.notify_camera_gear_due_returns() is True

        tasks.current_app = _app_with_no_logger()
        assert tasks.notify_camera_gear_due_returns() is True

        app, logged = _app_with_logger()
        tasks.current_app = app
        assert tasks.notify_camera_gear_due_returns() is True
        assert logged.get('exc')
    finally:
        tasks.current_app = orig_app


def test_lab_recipients_logging_variants(app_ctx, patcher):
    eq = types.SimpleNamespace(id=230, name='E', last_serviced_on=date.today() - timedelta(days=400), service_frequency='365')
    fake_lab = types.SimpleNamespace(); fake_lab.query = make_fake_query([eq])
    patcher(tasks, 'LabEquipment', fake_lab)

    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace(); fake_user.query = make_fake_query([u])
    patcher(tasks, 'User', fake_user)

    orig_app = tasks.current_app
    try:
        tasks.current_app = None
        assert tasks.notify_lab_equipment_service_reminders() is False

        tasks.current_app = _app_with_no_logger()
        assert tasks.notify_lab_equipment_service_reminders() is False

        app, logged = _app_with_logger()
        tasks.current_app = app
        assert tasks.notify_lab_equipment_service_reminders() is False
        assert logged.get('info')
    finally:
        tasks.current_app = orig_app


def test_lab_email_exception_logging_variants(app_ctx, patcher):
    eq = types.SimpleNamespace(id=240, name='E2', last_serviced_on=date.today() - timedelta(days=400), service_frequency='365')
    fake_lab = types.SimpleNamespace(); fake_lab.query = make_fake_query([eq])
    patcher(tasks, 'LabEquipment', fake_lab)

    u = types.SimpleNamespace(email='r@example.com', role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace(); fake_user.query = make_fake_query([u])
    patcher(tasks, 'User', fake_user)

    class BadEM2:
        def __init__(self, subject=None, to=None, body=None):
            pass
        def send(self):
            raise RuntimeError('boom2')

    patcher(tasks, 'EmailMessage', BadEM2)

    orig_app = tasks.current_app
    try:
        tasks.current_app = None
        assert tasks.notify_lab_equipment_service_reminders() is True

        tasks.current_app = _app_with_no_logger()
        assert tasks.notify_lab_equipment_service_reminders() is True

        app, logged = _app_with_logger()
        tasks.current_app = app
        assert tasks.notify_lab_equipment_service_reminders() is True
        assert logged.get('exc')
    finally:
        tasks.current_app = orig_app


def test_consumables_no_logger_on_app_suppresses_logging(app_ctx, patcher):
    fake_app = _app_with_no_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        fake_consumable = types.SimpleNamespace()
        fake_consumable.query = make_fake_query([])
        patcher(tasks, 'Consumable', fake_consumable)

        fake_user = types.SimpleNamespace()
        fake_user.query = make_fake_query([])
        patcher(tasks, 'User', fake_user)

        assert tasks.notify_consumables_expiring_this_week() is False
    finally:
        tasks.current_app = orig_app


def test_consumables_email_exception_with_no_logger_app(app_ctx, patcher):
    # Email send raises but app.logger is None -> suppressed
    fake_app = _app_with_no_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        c = types.SimpleNamespace(id=200, name='Foo', quantity=1, location=None, expires=date.today())
        fake_consumable = types.SimpleNamespace(); fake_consumable.query = make_fake_query([c])
        patcher(tasks, 'Consumable', fake_consumable)

        u = types.SimpleNamespace(email='admin-no-log@example.com', role=tasks.UserRole.ADMIN)
        fake_user = types.SimpleNamespace(); fake_user.query = make_fake_query([u])
        patcher(tasks, 'User', fake_user)

        class BadEM:
            def __init__(self, subject=None, to=None, body=None):
                pass
            def send(self):
                raise RuntimeError('smtp')

        patcher(tasks, 'EmailMessage', BadEM)

        assert tasks.notify_consumables_expiring_this_week() is True
    finally:
        tasks.current_app = orig_app


def test_camera_no_logger_on_app_suppresses_logging(app_ctx, patcher):
    fake_app = _app_with_no_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        fake_camera = types.SimpleNamespace(); fake_camera.query = make_fake_query([])
        patcher(tasks, 'CameraGear', fake_camera)
        assert tasks.notify_camera_gear_due_returns() is False
    finally:
        tasks.current_app = orig_app


def test_lab_no_logger_on_app_suppresses_logging(app_ctx, patcher):
    fake_app = _app_with_no_logger()
    orig_app = tasks.current_app
    tasks.current_app = fake_app
    try:
        fake_lab = types.SimpleNamespace(); fake_lab.query = make_fake_query([])
        patcher(tasks, 'LabEquipment', fake_lab)
        assert tasks.notify_lab_equipment_service_reminders() is False
    finally:
        tasks.current_app = orig_app


def test_notify_consumables_db_filter_fallback_and_user_filter_fallback(app_ctx, patcher):
    # Simulate DB .filter() raising so the code uses the .all() fallback
    c = types.SimpleNamespace(id=3, name="Tape", quantity=5, location=types.SimpleNamespace(name="Shelf B"), expires=date.today())
    fake_consumable = types.SimpleNamespace()
    fake_consumable.query = make_fake_query([c], raise_on_filter=True)
    patcher(tasks, "Consumable", fake_consumable)

    u = types.SimpleNamespace(email="admin-fallback@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u], raise_on_filter=True)
    patcher(tasks, "User", fake_user)

    sent = {}

    class FakeEM:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = to
            sent['body'] = body

        def send(self):
            sent['sent'] = True

    patcher(tasks, "EmailMessage", FakeEM)

    assert tasks.notify_consumables_expiring_this_week() is True
    assert sent.get('sent') is True


def test_notify_consumables_no_recipients_returns_false(app_ctx, patcher):
    c = types.SimpleNamespace(id=4, name="Glue", quantity=1, location=types.SimpleNamespace(name="Bin"), expires=date.today())
    fake_consumable = types.SimpleNamespace()
    fake_consumable.query = make_fake_query([c])
    patcher(tasks, "Consumable", fake_consumable)

    # Users exist but have no email addresses
    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    assert tasks.notify_consumables_expiring_this_week() is False


def test_notify_camera_gear_send_exception_logs(app_ctx, patcher):
    today = date.today()
    g = types.SimpleNamespace(id=30, name="Body", is_checked_out=True, return_date=today + timedelta(days=1), location=types.SimpleNamespace(name="Shelf"), checked_out_by=7, checked_out_by_user=None)

    fake_camera = types.SimpleNamespace()
    fake_camera.query = make_fake_query([g])
    patcher(tasks, "CameraGear", fake_camera)

    u = types.SimpleNamespace(email="admin-camera-ex@example.com", role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    class BadEM:
        def __init__(self, subject=None, to=None, body=None):
            pass

        def send(self):
            raise RuntimeError("smtp failure camera")

    patcher(tasks, "EmailMessage", BadEM)

    logged = {}

    from app import app as flask_app
    orig_exc = flask_app.logger.exception
    flask_app.logger.exception = lambda *a, **k: logged.setdefault('exc', True)

    try:
        assert tasks.notify_camera_gear_due_returns() is True
        assert logged.get('exc')
    finally:
        flask_app.logger.exception = orig_exc


def test_notify_lab_equipment_skips_problematic_record(app_ctx, patcher):
    # Create an equipment object that raises when accessing service_frequency
    class BadEq:
        id = 99
        name = "BadDevice"
        last_serviced_on = date.today() - timedelta(days=200)

        @property
        def service_frequency(self):
            raise RuntimeError("bad record")

    fake_lab = types.SimpleNamespace()
    fake_lab.query = make_fake_query([BadEq()])
    patcher(tasks, "LabEquipment", fake_lab)

    # Provide no recipients to ensure function returns False after skipping
    u = types.SimpleNamespace(email=None, role=tasks.UserRole.ADMIN)
    fake_user = types.SimpleNamespace()
    fake_user.query = make_fake_query([u])
    patcher(tasks, "User", fake_user)

    from app import app as flask_app
    logged = {}
    orig_info = flask_app.logger.info
    flask_app.logger.info = lambda *a, **k: logged.setdefault('info', True)

    try:
        assert tasks.notify_lab_equipment_service_reminders() is False
        assert logged.get('info')
    finally:
        flask_app.logger.info = orig_info
