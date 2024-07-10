from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy 인스턴스 생성
db = SQLAlchemy()

def init_app(app):
    """
    Flask 애플리케이션을 초기화하고 SQLAlchemy 인스턴스를 설정합니다.
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()
