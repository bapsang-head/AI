from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db import db, Base

# NutritionInfo 클래스는 음식의 영양 정보를 저장합니다.
class NutritionInfo(Base):
    __tablename__ = 'nutrition_info'  # 데이터베이스에서 사용할 테이블 이름
    id = Column(Integer, primary_key=True)  # 기본 키 열
    food = Column(String(50), unique=True, nullable=False)  # 음식 이름 (고유, null 불가)
    calories = Column(Integer, nullable=False)  # 칼로리 정보 (null 불가)
    protein = Column(Float, nullable=False)  # 단백질 정보 (null 불가)
    fat = Column(Float, nullable=False)  # 지방 정보 (null 불가)
    carbohydrates = Column(Float, nullable=False)  # 탄수화물 정보 (null 불가)

# UnitConversion 클래스는 특정 음식의 단위 변환 정보를 저장합니다.
class UnitConversion(Base):
    __tablename__ = 'unit_conversion'  # 데이터베이스에서 사용할 테이블 이름
    id = Column(Integer, primary_key=True)  # 기본 키 열
    food = Column(String, nullable=False)  # 음식 이름 (null 불가)
    unit = Column(String, nullable=False)  # 단위 (null 불가)
    grams = Column(Float, nullable=False)  # 그램으로 변환된 값 (null 불가)
    __table_args__ = (UniqueConstraint('food', 'unit', name='_food_unit_uc'),)  # food와 unit 조합에 대해 고유 제약 조건
