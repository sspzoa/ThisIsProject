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

    from .main import main_blueprint
    app.register_blueprint(main_blueprint)

    from .routes.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .routes.comment import comment_blueprint
    app.register_blueprint(comment_blueprint)

    from .routes.gpt import gpt_blueprint
    app.register_blueprint(gpt_blueprint)

    return app
