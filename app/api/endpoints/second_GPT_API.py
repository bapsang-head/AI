from flask import Blueprint, request, jsonify, Response
from app.services.gpt_service import generate_response
from app.services.rate_limiter import RateLimiter 
import json
import logging

logger = logging.getLogger(__name__)

second_GPT_API_blueprint = Blueprint('second_GPT_API', __name__)

# 하루에 최대 10회로 API 호출 제한을 초기화
rate_limiter = RateLimiter(max_calls=10)

@second_GPT_API_blueprint.route('/', methods=['POST'])
@rate_limiter.limit_api_calls  # API 호출 제한 데코레이터 적용
def process_second_GPT_API():
    try:
        logger.info(f"Received request: {request.data}")

        # API 키를 요청 헤더에서 가져오기
        gpt_api_key = request.headers.get('GPT-API-KEY')
        if not gpt_api_key:
            return jsonify({"error": "Missing GPT API key in headers"}), 400

        data = request.json
        if not data or 'data' not in data:
            logger.error("Invalid input: %s", data)
            return jsonify({"error": "Invalid input"}), 400

        logger.info(f"Received data: {data}")

        food_items = []
        for i in range(0, len(data["data"]), 2):
            food_items.append({
                "food": data["data"][i]["word"],
                "unit": data["data"][i + 1]["word"]
            })

        prompt = (
            f'The following is a list of foods and their units: {food_items}.\n'
            'For each food item, convert the unit to grams and provide the nutritional information per 100g. '
            'However, keep the original unit in the JSON output as provided in the input. '
            'Return the results in JSON format with each food item and its corresponding nutritional values. '
            'The JSON format should look like this: '
            '[{"food": "example_food", "unit": "example_unit", "gram": 100, '
            '"calories": 100, "carbohydrates": 100, '
            '"protein": 100, "fat": 100}]. '
            'Respond only with a valid JSON array. Do not include any additional text or explanation. '
            'The values should be realistic and accurate based on the food items.'
        )

        gpt_response = generate_response(prompt, gpt_api_key)  # API 키를 전달

        try:
            gpt_response_json = json.loads(gpt_response)
            response_json = json.dumps({"data": gpt_response_json}, ensure_ascii=False, indent=4)
            logger.info(f"Received response from OpenAI: {gpt_response}")
            return Response(response_json, mimetype='application/json')
        except json.JSONDecodeError:
            logger.error("Error converting response to JSON: No JSON object found in GPT response")
            return jsonify({
                "error": "Invalid JSON response from OpenAI",
                "gpt_response": gpt_response
            }), 500

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500
