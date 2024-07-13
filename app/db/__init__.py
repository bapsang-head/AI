from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Base를 정의합니다.
Base = db.Model

def init_app(app):
    db.init_app(app)
