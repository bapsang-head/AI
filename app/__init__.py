from flask import Flask
from flask_migrate import Migrate
from app.config import Config
from app.db import db, init_app 

migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    init_app(app) 
    migrate.init_app(app, db)

    from app.api.endpoints.diet import diet_bp
    app.register_blueprint(diet_bp, url_prefix='/api')

    return app
