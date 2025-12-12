import importlib
import sys
import types
from types import SimpleNamespace

import pytest


def _make_models_user_module(users):
    mod = types.ModuleType("models.user")

    class Query:
        def __init__(self, users):
            self._users = users

        def filter(self, *args, **kwargs):
            # ignore filtering expressions in tests
            return self

        def all(self):
            return list(self._users)

        def __iter__(self):
            return iter(self._users)

    class User:
        query = Query(users)

        def __init__(self, **kw):
            for k, v in kw.items():
                setattr(self, k, v)

    mod.User = User
    return mod


def _make_constants_module():
    mod = types.ModuleType("constants")

    class UserRole:
        ADMIN = "admin"
        TA = "ta"

    mod.UserRole = UserRole
    return mod


def test_send_no_mail_initialized(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", None)

    item = SimpleNamespace(id=1, name="Paper", quantity=1, location=None)

    # Should return early without raising
    assert mailmod.send_low_stock_alert(item) is None


def test_send_threshold_not_reached(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")

    # pretend mail is initialized
    monkeypatch.setattr(mailmod, "mail", object())

    # Patch EmailMessage so creation would raise if called
    def _raise_on_create(*args, **kwargs):
        raise AssertionError("EmailMessage should not be created when threshold not reached")

    monkeypatch.setattr(mailmod, "EmailMessage", _raise_on_create)

    item = SimpleNamespace(id=2, name="Ink", quantity=100, location=None)
    # threshold default is 5 so quantity 100 should skip sending
    assert mailmod.send_low_stock_alert(item) is None


def test_send_no_recipients(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    # Provide empty user list via fake models.user module
    sys.modules["models.user"] = _make_models_user_module([])
    sys.modules["constants"] = _make_constants_module()

    # Provide an EmailMessage stub that would record sends
    class FakeMessage:
        def __init__(self, *args, **kwargs):
            pass

        def send(self):
            raise AssertionError("send should not be called when there are no recipients")

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=3, name="Glue", quantity=1, location=None)
    assert mailmod.send_low_stock_alert(item) is None


def test_send_success_and_exception(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    # create two fake users: one admin with email, one without
    u1 = types.SimpleNamespace(email="admin@example.org", role="admin")
    u2 = types.SimpleNamespace(email=None, role="ta")
    sys.modules["models.user"] = _make_models_user_module([u1, u2])
    sys.modules["constants"] = _make_constants_module()

    sent = {}

    class FakeMessage:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = list(to) if to else []
            sent['body'] = body

        def send(self):
            sent['sent'] = True

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=4, name="Tape", quantity=1, location=types.SimpleNamespace(name="Store"))
    # run should not raise and should have called send
    assert mailmod.send_low_stock_alert(item) is None
    assert sent.get('sent') is True
    assert "Tape" in sent['subject'] or "Low stock alert" in sent['subject']

    # Now ensure exceptions from send are swallowed
    class BadMessage(FakeMessage):
        def send(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(mailmod, "EmailMessage", BadMessage)
    # Should not raise
    assert mailmod.send_low_stock_alert(item) is None


def test_threshold_env_invalid_and_send(monkeypatch):
    # If LOW_STOCK_THRESHOLD is non-int, fallback to default 5
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setenv("LOW_STOCK_THRESHOLD", "not-an-int")
    monkeypatch.setattr(mailmod, "mail", object())

    u = types.SimpleNamespace(email="a@x.com", role="admin")
    sys.modules["models.user"] = _make_models_user_module([u])
    sys.modules["constants"] = _make_constants_module()

    sent = {}

    class FakeMessage:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = list(to) if to else []

        def send(self):
            sent['sent'] = True

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=5, name="Glue", quantity=4, location=None)
    assert mailmod.send_low_stock_alert(item) is None
    assert sent.get('sent') is True


def test_quantity_uninterpretable(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    # set quantity to something that int() can't parse
    item = SimpleNamespace(id=6, name="Strange", quantity="xyz", location=None)

    # If EmailMessage is created, fail the test
    def _raise_on_create(*a, **k):
        raise AssertionError("EmailMessage should not be created when quantity is uninterpretable")

    monkeypatch.setattr(mailmod, "EmailMessage", _raise_on_create)
    # Should return silently
    assert mailmod.send_low_stock_alert(item) is None


def test_import_failure_returns(monkeypatch):
    # If importing models.user or constants fails, function should return
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    # Ensure modules are not present
    monkeypatch.delitem(sys.modules, "models.user", raising=False)
    monkeypatch.delitem(sys.modules, "constants", raising=False)

    # If EmailMessage is created, fail the test
    def _raise_on_create(*a, **k):
        raise AssertionError("EmailMessage should not be created when imports fail")

    monkeypatch.setattr(mailmod, "EmailMessage", _raise_on_create)

    item = SimpleNamespace(id=7, name="Widget", quantity=1, location=None)
    assert mailmod.send_low_stock_alert(item) is None


def test_filter_raises_uses_all_fallback(monkeypatch):
    # Create a models.user module where User.query.filter raises
    mod = types.ModuleType("models.user")

    class Query:
        def filter(self, *a, **k):
            raise Exception("filter not supported")

        def all(self):
            return [types.SimpleNamespace(email="x@x.com", role="admin")]

    class User:
        query = Query()

    mod.User = User
    sys.modules["models.user"] = mod
    sys.modules["constants"] = _make_constants_module()

    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    sent = {}

    class FakeMessage:
        def __init__(self, subject=None, to=None, body=None):
            sent['to'] = list(to) if to else []

        def send(self):
            sent['sent'] = True

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=8, name="Paper", quantity=1, location=None)
    assert mailmod.send_low_stock_alert(item) is None
    assert sent.get('sent') is True


def test_send_exception_logs(monkeypatch):
    # If EmailMessage.send raises, the exception should be logged via current_app.logger.exception
    from flask import Flask

    app = Flask(__name__)
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    # create a message that raises on send
    class BadMessage:
        def __init__(self, *a, **k):
            pass

        def send(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(mailmod, "EmailMessage", BadMessage)

    called = []

    def _log_exception(*a, **k):
        called.append(True)

    app.logger.exception = _log_exception

    item = SimpleNamespace(id=9, name="Stapler", quantity=1, location=None)
    with app.app_context():
        # Should not raise, but logger.exception should be called
        assert mailmod.send_low_stock_alert(item) is None
    assert called, "logger.exception was not called"


def test_threshold_env_parsed(monkeypatch):
    # If LOW_STOCK_THRESHOLD is a valid int, it should be parsed and used
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setenv("LOW_STOCK_THRESHOLD", "10")
    monkeypatch.setattr(mailmod, "mail", object())

    u = types.SimpleNamespace(email="b@x.com", role="admin")
    sys.modules["models.user"] = _make_models_user_module([u])
    sys.modules["constants"] = _make_constants_module()

    called = {}

    class FakeMessage:
        def __init__(self, subject=None, to=None, body=None):
            called['subject'] = subject

        def send(self):
            called['sent'] = True

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=10, name="Ribbon", quantity=1, location=None)
    assert mailmod.send_low_stock_alert(item) is None
    assert called.get('sent') is True


def test_send_exception_no_logger(monkeypatch):
    # If EmailMessage.send raises but current_app.logger is falsy, code should return silently
    from flask import Flask

    app = Flask(__name__)
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    class BadMessage:
        def __init__(self, *a, **k):
            pass

        def send(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(mailmod, "EmailMessage", BadMessage)

    # make logger falsy
    app.logger = None

    item = SimpleNamespace(id=11, name="Staples", quantity=1, location=None)
    with app.app_context():
        # Should not raise
        assert mailmod.send_low_stock_alert(item) is None


def test_threshold_arg_provided_skips_env(monkeypatch):
    # When threshold is provided as an argument the env var path is skipped
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setenv("LOW_STOCK_THRESHOLD", "not-an-int")
    monkeypatch.setattr(mailmod, "mail", object())

    u = types.SimpleNamespace(email="c@x.com", role="admin")
    sys.modules["models.user"] = _make_models_user_module([u])
    sys.modules["constants"] = _make_constants_module()

    recorded = {}

    class FakeMessage:
        def __init__(self, subject=None, to=None, body=None):
            recorded['subject'] = subject

        def send(self):
            recorded['sent'] = True

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=12, name="Ribbon", quantity=1, location=None)
    # Passing threshold should skip reading LOW_STOCK_THRESHOLD env entirely
    assert mailmod.send_low_stock_alert(item, threshold=10) is None
    assert recorded.get('sent') is True
