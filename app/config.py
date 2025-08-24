import os

class Config:
    # Instance-relative SQLite at instance/app.db
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "SQLALCHEMY_DATABASE_URI",
        "sqlite:///app.db"  # instance/app.db
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False