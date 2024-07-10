from flask import Flask
from app.api.endpoints.diet import diet_bp
from app.db import init_app, db

def create_app():
    """
    Flask 애플리케이션을 생성하고 초기화합니다.
    """
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nutrition.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # 데이터베이스 초기화
    init_app(app)
    
    app.register_blueprint(diet_bp)
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
