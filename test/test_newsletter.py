import pytest
import werkzeug
from app import create_app, db, mail
from app.models import NewsletterSubscriber

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
    # Re-initialize mail to apply updated config
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


def test_contact_form_newsletter(client, app):
    with app.app_context():
        with mail.record_messages() as outbox:
            resp = client.post('/submit', data={
            'form_id': 'contact',
            'name': 'Alice',
            'email': 'alice@example.com',
            'message': 'Hello',
            'accept_policy': 'on',
            'newsletter': 'on'
            }, follow_redirects=True)
            assert resp.status_code == 200
            assert b'Your message has been sent. Thank you!' in resp.data
            sub = NewsletterSubscriber.query.filter_by(email='alice@example.com').first()
            assert sub is not None
            assert sub.form_tag == 'contact'
            assert len(outbox) == 2
            assert any(m.subject == 'New Newsletter Subscriber' and 'Source: contact' in m.body for m in outbox)


def test_newsletter_form(client, app):
    with app.app_context():
        with mail.record_messages() as outbox:
            resp = client.post('/submit', data={
            'form_id': 'newsletter',
            'name': 'Bob',
            'email': 'bob@example.com',
            'accept_policy': 'on'
            }, follow_redirects=True)
            assert resp.status_code == 200
            assert b'Thanks for subscribing!' in resp.data
            sub = NewsletterSubscriber.query.filter_by(email='bob@example.com').first()
            assert sub is not None
            assert sub.form_tag == 'footer'
            assert len(outbox) == 1
            assert 'Source: newsletter' in outbox[0].body