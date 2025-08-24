import pytest
import werkzeug
from app import create_app, db, mail

if not hasattr(werkzeug, "__version__"):
    werkzeug.__version__ = "3"


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        SECRET_KEY='test-secret',
        TESTING=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///:memory:',
        CONTACT_RECIPIENT='admin@example.com',
        MAIL_SUPPRESS_SEND=True,
        MAIL_DEFAULT_SENDER='noreply@example.com',
    )
    mail.init_app(app)
    app.secret_key = app.config['SECRET_KEY']
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_footer_newsletter_never_redirects_to_submit(client):
    headers = {"Referer": "http://localhost/submit"}
    resp = client.post(
        "/submit",
        data={
            "form_id": "newsletter",
            "name": "Bob",
            "email": "bob@example.com",
            "accept_policy": "on",
        },
        headers=headers,
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)
    assert "/redirect" in resp.headers["Location"]
    assert "target=" in resp.headers["Location"]
    assert "%2Fsubmit" not in resp.headers["Location"]


def test_footer_newsletter_db_failure_shows_error(client, monkeypatch):
    from sqlalchemy.exc import OperationalError

    def boom(*args, **kwargs):
        raise OperationalError("X", "Y", "Z")

    monkeypatch.setattr("app.routes.db.session.execute", boom)
    headers = {"Referer": "http://localhost/submit"}
    resp = client.post(
        "/submit",
        data={
            "form_id": "newsletter",
            "name": "Bob",
            "email": "bob@example.com",
            "accept_policy": "on",
        },
        headers=headers,
        follow_redirects=True,
    )
    assert b"We couldn&#39;t save your subscription" in resp.data
    assert b"Thanks for subscribing!" not in resp.data