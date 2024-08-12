from flask import Blueprint, request, jsonify, Response
from app.services.gpt_service import generate_response
from app.services.rate_limiter import RateLimiter
import json
import logging

logger = logging.getLogger(__name__)

second_GPT_API_blueprint = Blueprint('second_GPT_API', __name__)

# 하루에 최대 100회로 API 호출 제한을 초기화
rate_limiter = RateLimiter(max_calls=100)

@second_GPT_API_blueprint.route('/', methods=['POST'])
@rate_limiter.limit_api_calls
def process_second_GPT_API():
    """
    주어진 음식 항목과 단위를 바탕으로 단위를 그램으로 변환하고,
    100g 당 영양 정보를 제공하는 API 엔드포인트.
    하루에 100회까지 호출이 가능하며, 그 이상 호출 시 429 에러를 반환합니다.
    """
    data = request.json

    logger.info(f"Received data: {data}")

    food_items = []
    for i in range(0, len(data["data"]), 2):
        food_items.append({
            "food": data["data"][i]["word"],
            "unit": data["data"][i + 1]["word"]
        })

    # GPT에게 전달할 프롬프트 생성
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

    # GPT 모델에 프롬프트 전달하고 결과 수신
    gpt_response = generate_response(prompt)

    try:
        # GPT 응답을 JSON으로 파싱
        gpt_response_json = json.loads(gpt_response)
        response_json = json.dumps({"data": gpt_response_json}, ensure_ascii=False, indent=4)
        logger.info(f"Received response from OpenAI: {gpt_response}")
        return Response(response_json, mimetype='application/json')
    except json.JSONDecodeError:
        # JSON 파싱 실패 시 에러 응답
        logger.error("Error converting response to JSON: No JSON object found in GPT response")
        return jsonify({
            "error": "Invalid JSON response from OpenAI",
            "gpt_response": gpt_response
        }), 500

