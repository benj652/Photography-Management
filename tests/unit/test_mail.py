# Test file: relax some pylint checks that are noisy for tests
# pylint: disable=missing-module-docstring,missing-function-docstring,missing-class-docstring,too-few-public-methods
# pylint: disable=redefined-builtin,unused-argument,unused-variable,no-member,wrong-import-order,reimported,import-outside-toplevel,unused-import,broad-exception-raised

import builtins
import importlib
import sys
import types
from types import ModuleType, SimpleNamespace

import pytest


def _make_item(quantity, name="Widget", item_id=1, location_name=None):
    class Loc:
        def __init__(self, name):
            self.name = name

    class Item:
        def __init__(self):
            self.id = item_id
            self.name = name
            self.quantity = quantity
            self.location = Loc(location_name) if location_name else None

    return Item()


def test_quantity_above_threshold_returns_false(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")

    itm = _make_item(10)
    # ensure mail state won't affect this branch
    monkeypatch.setattr(mailmod, "mail", object(), raising=False)

    assert mailmod.send_low_stock_alert(itm) is False


def test_quantity_uninterpretable_returns_false(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")

    itm = _make_item("notanint")
    monkeypatch.setattr(mailmod, "mail", object(), raising=False)

    assert mailmod.send_low_stock_alert(itm) is False


def test_mail_not_initialized_returns_false(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")

    itm = _make_item(1)
    # ensure mail is None so function returns False after quantity check
    monkeypatch.setattr(mailmod, "mail", None, raising=False)

    assert mailmod.send_low_stock_alert(itm) is False


def test_import_failure_returns_false(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")

    itm = _make_item(1)

    # ensure mail initialized so import happens after
    monkeypatch.setattr(mailmod, "mail", object(), raising=False)

    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        # simulate ImportError for the relative models/constants imports
        if name.startswith("website.models") or name.startswith("website.constants"):
            raise ImportError("forced")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    try:
        assert mailmod.send_low_stock_alert(itm) is False
    finally:
        monkeypatch.setattr(builtins, "__import__", real_import)


def test_recipients_query_filter_success_sends_email(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")

    itm = _make_item(1)

    # create fake models module with User and query behaviour
    mod = ModuleType("website.models")

    class FakeUser:
        def __init__(self, email, role):
            self.email = email
            self.role = role

    class FakeQuery:
        def __init__(self, users):
            self._users = users

        def filter(self, *args, **kwargs):
            return self

        def all(self):
            return self._users

    # attach a query object on the class to mimic SQLAlchemy pattern
    FakeUser.query = FakeQuery([FakeUser("a@example.com", "ADMIN")])

    # fake constants module
    class UR:
        ADMIN = "ADMIN"
        TA = "TA"

    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", FakeUser, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", UR, raising=False)

    sent = {}

    class FakeMsg:
        def __init__(self, subject=None, to=None, body=None):
            sent["subject"] = subject
            sent["to"] = to
            sent["body"] = body

        def send(self):
            sent["sent"] = True

    monkeypatch.setattr(mailmod, "mail", object(), raising=False)
    monkeypatch.setattr(mailmod, "EmailMessage", FakeMsg)

    try:
        assert mailmod.send_low_stock_alert(itm) is True
        assert sent.get("sent") is True
        assert "Low stock alert" in sent["subject"]
    finally:
        # monkeypatch will restore attributes; nothing to clean in sys.modules
        pass


def test_recipients_fallback_and_no_recipients(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")

    itm = _make_item(1)

    # fake models with query.filter raising and query.all returning users without emails
    mod = ModuleType("website.models")

    class FakeUser2:
        def __init__(self, email, role):
            self.email = email
            self.role = role

    class BadQuery:
        def filter(self, *a, **k):
            raise Exception("no filter")

        def all(self):
            return [FakeUser2(None, "ADMIN")]

    FakeUser2.query = BadQuery()

    class UR2:
        ADMIN = "ADMIN"
        TA = "TA"

    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", FakeUser2, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", UR2, raising=False)

    monkeypatch.setattr(mailmod, "mail", object(), raising=False)

    try:
        assert mailmod.send_low_stock_alert(itm) is False
    finally:
        pass


def test_send_failure_returns_true_after_logging(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")

    itm = _make_item(1)

    # fake models module with recipient
    mod = ModuleType("website.models")

    class FakeUser3:
        def __init__(self, email, role):
            self.email = email
            self.role = role

    class Query3:
        def filter(self, *a, **k):
            return self

        def all(self):
            return [FakeUser3("a@example.com", "ADMIN")]

    FakeUser3.query = Query3()

    class UR3:
        ADMIN = "ADMIN"
        TA = "TA"

    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", FakeUser3, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", UR3, raising=False)

    class ExplodingMsg:
        def __init__(self, subject=None, to=None, body=None):
            pass

        def send(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(mailmod, "mail", object(), raising=False)
    monkeypatch.setattr(mailmod, "EmailMessage", ExplodingMsg)

    # send raises, but function should return True (attempted)
    assert mailmod.send_low_stock_alert(itm) is True

def _make_models_user_module(users):
    mod = types.ModuleType("website.models")

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
    mod = types.ModuleType("website.constants")

    class UserRole:
        ADMIN = "admin"
        TA = "ta"

    mod.UserRole = UserRole
    return mod


def test_send_no_mail_initialized(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", None)

    item = SimpleNamespace(id=1, name="Paper", quantity=1, location=None)

    # Should return early without raising; returns False when skipped
    assert mailmod.send_low_stock_alert(item) is False


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
    assert mailmod.send_low_stock_alert(item) is False


def test_send_no_recipients(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    # Provide empty user list via fake models.user module
    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", _make_models_user_module([]).User, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", _make_constants_module().UserRole, raising=False)

    # Provide an EmailMessage stub that would record sends
    class FakeMessage:
        def __init__(self, *args, **kwargs):
            pass

        def send(self):
            raise AssertionError("send should not be called when there are no recipients")

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=3, name="Glue", quantity=1, location=None)
    assert mailmod.send_low_stock_alert(item) is False


def test_send_success_and_exception(monkeypatch):
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    # create two fake users: one admin with email, one without
    u1 = types.SimpleNamespace(email="admin@example.org", role="admin")
    u2 = types.SimpleNamespace(email=None, role="ta")
    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", _make_models_user_module([u1, u2]).User, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", _make_constants_module().UserRole, raising=False)

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
    assert mailmod.send_low_stock_alert(item) is True
    assert sent.get('sent') is True
    assert "Tape" in sent['subject'] or "Low stock alert" in sent['subject']

    # Now ensure exceptions from send are swallowed
    class BadMessage(FakeMessage):
        def send(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(mailmod, "EmailMessage", BadMessage)
    # Should not raise
    assert mailmod.send_low_stock_alert(item) is True


def test_threshold_env_invalid_and_send(monkeypatch):
    # If LOW_STOCK_THRESHOLD is non-int, fallback to default 5
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setenv("LOW_STOCK_THRESHOLD", "not-an-int")
    monkeypatch.setattr(mailmod, "mail", object())

    u = types.SimpleNamespace(email="a@x.com", role="admin")
    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", _make_models_user_module([u]).User, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", _make_constants_module().UserRole, raising=False)

    sent = {}

    class FakeMessage:
        def __init__(self, subject=None, to=None, body=None):
            sent['subject'] = subject
            sent['to'] = list(to) if to else []

        def send(self):
            sent['sent'] = True

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=5, name="Glue", quantity=4, location=None)
    assert mailmod.send_low_stock_alert(item) is True
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
    assert mailmod.send_low_stock_alert(item) is False


def test_import_failure_returns(monkeypatch):
    # If importing models.user or constants fails, function should return
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setattr(mailmod, "mail", object())

    # Ensure modules are not present
    monkeypatch.delitem(sys.modules, "website.models", raising=False)
    monkeypatch.delitem(sys.modules, "website.constants", raising=False)

    # If EmailMessage is created, fail the test
    def _raise_on_create(*a, **k):
        raise AssertionError("EmailMessage should not be created when imports fail")

    monkeypatch.setattr(mailmod, "EmailMessage", _raise_on_create)

    item = SimpleNamespace(id=7, name="Widget", quantity=1, location=None)
    assert mailmod.send_low_stock_alert(item) is False


def test_filter_raises_uses_all_fallback(monkeypatch):
    # Create a models.user module where User.query.filter raises
    class Query:
        def filter(self, *a, **k):
            raise Exception("filter not supported")

        def all(self):
            return [types.SimpleNamespace(email="x@x.com", role="admin")]

    class User:
        query = Query()

    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", User, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", _make_constants_module().UserRole, raising=False)

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
    assert mailmod.send_low_stock_alert(item) is True
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
    # ensure recipients exist so we exercise the send exception logging path
    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", _make_models_user_module([types.SimpleNamespace(email='x@x.com', role='admin')]).User, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", _make_constants_module().UserRole, raising=False)
    with app.app_context():
        # Should not raise, but logger.exception should be called
        assert mailmod.send_low_stock_alert(item) is True

    assert called, "logger.exception was not called"


def test_threshold_env_parsed(monkeypatch):
    # If LOW_STOCK_THRESHOLD is a valid int, it should be parsed and used
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setenv("LOW_STOCK_THRESHOLD", "10")
    monkeypatch.setattr(mailmod, "mail", object())

    u = types.SimpleNamespace(email="b@x.com", role="admin")
    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", _make_models_user_module([u]).User, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", _make_constants_module().UserRole, raising=False)

    called = {}

    class FakeMessage:
        def __init__(self, subject=None, to=None, body=None):
            called['subject'] = subject

        def send(self):
            called['sent'] = True

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=10, name="Ribbon", quantity=1, location=None)
    assert mailmod.send_low_stock_alert(item) is True
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
    # ensure recipients exist so we exercise the send exception path
    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", _make_models_user_module([types.SimpleNamespace(email='y@x.com', role='admin')]).User, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", _make_constants_module().UserRole, raising=False)
    with app.app_context():
        # Should not raise and should return True since we attempted to send
        assert mailmod.send_low_stock_alert(item) is True


def test_threshold_arg_provided_skips_env(monkeypatch):
    # When threshold is provided as an argument the env var path is skipped
    mailmod = importlib.import_module("website.utils.mail")
    monkeypatch.setenv("LOW_STOCK_THRESHOLD", "not-an-int")
    monkeypatch.setattr(mailmod, "mail", object())

    u = types.SimpleNamespace(email="c@x.com", role="admin")
    models_mod = importlib.import_module("website.models")
    const_mod = importlib.import_module("website.constants")
    monkeypatch.setattr(models_mod, "User", _make_models_user_module([u]).User, raising=False)
    monkeypatch.setattr(const_mod, "UserRole", _make_constants_module().UserRole, raising=False)

    recorded = {}

    class FakeMessage:
        def __init__(self, subject=None, to=None, body=None):
            recorded['subject'] = subject

        def send(self):
            recorded['sent'] = True

    monkeypatch.setattr(mailmod, "EmailMessage", FakeMessage)

    item = SimpleNamespace(id=12, name="Ribbon", quantity=1, location=None)
    # Passing threshold should skip reading LOW_STOCK_THRESHOLD env entirely
    assert mailmod.send_low_stock_alert(item, threshold=10) is True
    assert recorded.get('sent') is True
