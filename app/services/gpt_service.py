import openai
import json
import logging
from app.config import Config
from app.db.models import NutritionInfo, UnitConversion
from app.db import db

openai.api_key = Config.OPENAI_API_KEY

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_response(prompt, max_tokens=200, temperature=0.7):
    """
    GPT 모델을 사용하여 프롬프트에 대한 응답을 생성합니다.
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

def extract_json(response):
    """
    응답에서 JSON 부분을 추출합니다.
    """
    try:
        start_idx = response.index('{')
        end_idx = response.rindex('}') + 1
        json_str = response[start_idx:end_idx]
        return json.loads(json_str)
    except (ValueError, json.JSONDecodeError) as e:
        logger.error(f"Error extracting JSON: {e}")
        raise ValueError("Failed to extract JSON from response")

def parse_input_data(input_data):
    entities = []

    if isinstance(input_data, dict):
        data_list = input_data.get("data", [])
    elif isinstance(input_data, list):
        data_list = input_data
    else:
        raise ValueError("Invalid input data format")

    current_entity = {}
    for item in data_list:
        if item["tag"].startswith("B-FOOD"):
            if current_entity:
                entities.append(current_entity)
                current_entity = {}
            current_entity["food"] = item["word"]
        elif item["tag"].startswith("B-QTY"):
            current_entity["qty"] = item["word"]
        elif item["tag"].startswith("B-UNIT"):
            current_entity["unit"] = item["word"]

    if current_entity:
        entities.append(current_entity)

    return entities

def convert_to_grams(unit, food):
    try:
        # 기존 변환 값을 확인합니다
        conversion = UnitConversion.query.filter_by(unit=unit, food=food).first()
        if conversion:
            return conversion.grams

        # GPT에게 변환 요청을 보냅니다
        prompt = f"Converts one {unit} of {food} into grams and provides the results in JSON format using the 'grams' key."
        response = generate_response(prompt, max_tokens=300)
        logger.debug(f"GPT Response: {response}")

        conversion_info = extract_json(response)  # JSON 부분을 추출합니다
        
        grams_per_unit = conversion_info.get("grams")
        if grams_per_unit is None:
            raise ValueError("No grams value found in the response")

        if not isinstance(grams_per_unit, (int, float)) or grams_per_unit <= 0:
            raise ValueError(f"Invalid grams value received: {grams_per_unit}")

        # 새로운 변환 값을 추가합니다
        new_conversion = UnitConversion(unit=unit, food=food, grams=grams_per_unit)
        db.session.add(new_conversion)
        db.session.commit()

        return grams_per_unit
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse unit conversion: {e}")
        return {"error": f"Failed to parse unit conversion: {str(e)}"}


def get_nutrition_info(food):
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
        logger.debug(f"GPT Response: {response}")
        response = response.strip("```json").strip("```")  # ```json으로 감싸진 부분을 제거합니다.
        nutrition_info = extract_json(response)  # JSON 부분을 추출합니다.

        # Ensure values are converted to appropriate types
        def parse_value(value):
            if isinstance(value, str):
                return float(value.replace(" kcal", "").replace("g", "").strip())
            return float(value)

        calories = parse_value(nutrition_info["calories"])
        protein = parse_value(nutrition_info["protein"])
        fat = parse_value(nutrition_info["fat"])
        carbohydrates = parse_value(nutrition_info["carbohydrates"])

        new_nutrition = NutritionInfo(
            food=food,
            calories=calories,
            protein=protein,
            fat=fat,
            carbohydrates=carbohydrates
        )
        db.session.add(new_nutrition)
        db.session.commit()
        return {
            "calories": calories,
            "protein": protein,
            "fat": fat,
            "carbohydrates": carbohydrates
        }
    except (ValueError, KeyError) as e:
        logger.error(f"Failed to parse nutrition information for {food}: {e}")
        return {"error": f"Failed to parse nutrition information: {str(e)}"}


def process_data(data):
    input_data = data.get("data")
    if not input_data or not isinstance(input_data, list):
        return {"error": "Invalid input data"}

    entities = parse_input_data(input_data)
    results = []

    for entity in entities:
        food = entity.get("food")
        qty = entity.get("qty")
        unit = entity.get("unit")

        if not all([food, qty, unit]):
            results.append({
                "error": "Missing required entity information."
            })
            continue

        gram_qty = convert_to_grams(unit, food)
        nutrition_info = get_nutrition_info(food)
        results.append({
            "entities": {
                "FOOD": food,
                "GRAM_QTY": gram_qty,
                "QTY": qty,
                "UNIT": unit
            },
            "nutrition_info": nutrition_info,
            "task_id": f"task_{len(results) + 1}"
        })

    return results
