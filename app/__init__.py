from flask import Flask
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

mail = Mail()
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    
    # Default config (points to instance/app.db)
    app.config.from_object(Config)

    # Optional: load instance config if present (won't exist in repo by default)
    app.config.from_pyfile("config.py", silent=True)

    # Defaults for secret key
    app.config.setdefault("SECRET_KEY", "dev")

    app.secret_key = app.config["SECRET_KEY"]

    mail.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from .routes import main
    app.register_blueprint(main)

    return app
