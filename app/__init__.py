from flask import Flask
from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=True)
    app.secret_key = app.config['SECRET_KEY']

    mail.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    return app
