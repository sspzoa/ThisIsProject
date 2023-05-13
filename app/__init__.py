from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(config)
    
    db.init_app(app)
    Migrate(app, db)

    from .routes import main_blueprint
    app.register_blueprint(main_blueprint)

    return app
