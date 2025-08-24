from datetime import datetime
from app import db


class NewsletterSubscriber(db.Model):
    __tablename__ = "newsletter_subscriber"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    form_tag = db.Column(db.String(50), nullable=True)  # e.g. 'contact' or 'footer'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)