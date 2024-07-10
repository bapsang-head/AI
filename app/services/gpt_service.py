import openai
import json
import logging
from app.config import OPENAI_API_KEY
from app.db.models import NutritionInfo, UnitConversion, db

openai.api_key = OPENAI_API_KEY

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_response(prompt, max_tokens=150, temperature=0.7):
    """
    GPT-3.5-turbo 모델을 사용하여 프롬프트에 대한 응답을 생성합니다.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logger.error(f"Error in generating response: {e}")
        return str(e)

def parse_input_data(input_data):
    """
    입력 데이터를 파싱하여 음식, 수량, 단위를 추출합니다.
    """
    entities = []
    current_entity = {}
    
    for item in input_data:
        if item["tag"].startswith("B-FOOD"):
            if current_entity:
                entities.append(current_entity)
            current_entity = {"FOOD": item["word"], "QTY": "", "UNIT": ""}
        elif item["tag"] == "B-QTY":
            current_entity["QTY"] = item["word"]
        elif item["tag"] == "B-UNIT":
            current_entity["UNIT"] = item["word"]

    if current_entity:
        entities.append(current_entity)

    return entities

korean_to_arabic = {
    "영": 0, "하나": 1, "둘": 2, "셋": 3, "넷": 4, "다섯": 5, "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9,
    "한": 1, "두": 2, "세": 3, "네": 4, "다섯": 5, "여섯": 6, "일곱": 7, "여덟": 8, "아홉": 9
}

def convert_korean_to_arabic(korean_number):
    """
    한국어 숫자를 아라비아 숫자로 변환합니다.
    """
    return korean_to_arabic.get(korean_number, None)

def convert_to_grams(unit, qty):
    """
    단위 변환 정보를 데이터베이스에서 조회하고, 없으면 GPT API를 통해 가져옵니다.
    """
    qty_number = convert_korean_to_arabic(qty)
    if qty_number is None:
        return {"error": f"Could not convert '{qty}' to a number"}
    
    conversion = UnitConversion.query.filter_by(unit=unit).first()
    if conversion:
        return qty_number * conversion.grams

    prompt = f"Convert {qty_number} {unit} to grams and provide the result in JSON format with a key 'grams'."
    response = generate_response(prompt)
    try:
        conversion_info = json.loads(response)
        grams = conversion_info["grams"]
        new_conversion = UnitConversion(unit=unit, grams=grams)
        db.session.add(new_conversion)
        db.session.commit()
        return grams
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse unit conversion: {e}")
        return {"error": f"Failed to parse unit conversion: {str(e)}"}

def get_nutrition_info(food):
    """
    영양 정보를 데이터베이스에서 조회하고, 없으면 GPT API를 통해 가져옵니다.
    """
    nutrition = NutritionInfo.query.filter_by(food=food).first()
    if nutrition:
        return {
            "calories": nutrition.calories,
            "protein": nutrition.protein,
            "fat": nutrition.fat,
            "carbohydrates": nutrition.carbohydrates
        }
    
    prompt = f"Provide the nutritional information for {food} in JSON format. The keys should be 'calories', 'protein', 'fat', and 'carbohydrates'."
    response = generate_response(prompt)
    try:
        logger.debug(f"GPT Response for {food}: {response}")
        nutrition_info = json.loads(response)
        new_nutrition = NutritionInfo(
            food=food,
            calories=nutrition_info["calories"],
            protein=nutrition_info["protein"],
            fat=nutrition_info["fat"],
            carbohydrates=nutrition_info["carbohydrates"]
        )
        db.session.add(new_nutrition)
        db.session.commit()
        return nutrition_info
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse nutrition information for {food}: {e}")
        return {"error": f"Failed to parse nutrition information: {str(e)}"}

def process_data(input_data):
    """
    입력 데이터를 처리하여 음식, 수량, 단위를 추출하고 영양 정보를 추가합니다.
    """
    entities = parse_input_data(input_data)
    response_data = []

    for idx, entity in enumerate(entities, start=1):
        food = entity["FOOD"]
        qty = entity["QTY"]
        unit = entity["UNIT"]
        gram_qty = convert_to_grams(unit, qty)
        
        response_data.append({
            "task_id": f"task_{idx}",
            "entities": {
                "FOOD": food,
                "QTY": qty,
                "GRAM_QTY": gram_qty,
                "UNIT": unit
            },
            "nutrition_info": get_nutrition_info(food)
        })

    return response_data
