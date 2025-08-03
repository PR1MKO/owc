from datetime import datetime

from . import db


class NewsletterSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    email = db.Column(db.String(120), unique=True, nullable=False)
    form_tag = db.Column(db.String(50), nullable=False, default='newsletter')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)