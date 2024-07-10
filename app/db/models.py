from app.db import db

class NutritionInfo(db.Model):
    """
    영양 정보 모델을 정의합니다.
    """
    id = db.Column(db.Integer, primary_key=True)  # 고유 ID
    food = db.Column(db.String(50), unique=True, nullable=False)  # 음식 이름
    calories = db.Column(db.Integer, nullable=False)  # 칼로리
    protein = db.Column(db.Float, nullable=False)  # 단백질
    fat = db.Column(db.Float, nullable=False)  # 지방
    carbohydrates = db.Column(db.Float, nullable=False)  # 탄수화물

class UnitConversion(db.Model):
    """
    단위 변환 정보를 정의합니다.
    """
    id = db.Column(db.Integer, primary_key=True)  # 고유 ID
    unit = db.Column(db.String(50), unique=True, nullable=False)  # 단위 이름
    grams = db.Column(db.Float, nullable=False)  # 단위 당 그램 수
