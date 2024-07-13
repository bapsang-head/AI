from sqlalchemy import Column, Integer, String, Float, UniqueConstraint
from app.db import db, Base

class NutritionInfo(Base):
    __tablename__ = 'nutrition_info'
    id = Column(Integer, primary_key=True)
    food = Column(String(50), unique=True, nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=False)
    fat = Column(Float, nullable=False)
    carbohydrates = Column(Float, nullable=False)

class UnitConversion(Base):
    __tablename__ = 'unit_conversion'
    id = Column(Integer, primary_key=True)
    food = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    grams = Column(Float, nullable=False)
    __table_args__ = (UniqueConstraint('food', 'unit', name='_food_unit_uc'),)
