from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("config.py", silent=True)

    # Defaults for secret key and database
    app.config.setdefault("SECRET_KEY", "dev")
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///owc.db")
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    app.secret_key = app.config["SECRET_KEY"]

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import main
    app.register_blueprint(main)

    return app
