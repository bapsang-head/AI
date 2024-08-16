from flask import Blueprint, request, jsonify, Response
from app.services.gpt_service import generate_response
from app.services.rate_limiter import RateLimiter 
from app.models.RAG.rag import RAG
import json
import logging

logger = logging.getLogger(__name__)
rag_instance = RAG()

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

        # 음식 이름만 추출하여 리스트 생성
        food_names = [item['food'] for item in food_items]

        # 영양 정보 검색 및 프롬프트에 추가
        all_nutrition_info = []
        for food_name in food_names:
            nutrition_info = rag_instance.search_nutrition_info(food_name)
            if nutrition_info:
                all_nutrition_info.extend(nutrition_info)

        # 프롬프트 설정
        prompt = (
            f"Here is a list of foods and their units: {food_items}.\n"
            "For each food, the unit is converted to grams and provided in a category called gram. Additionally, nutritional information is provided per 100g."
            "The original units should be preserved in the JSON output, reflecting the input format."
            "Additionally, use the following nutritional information retrieved from our database:\n"
            + "\n".join(all_nutrition_info) + "\n"
            "Returns results strictly in JSON format:\n"
            '[{"food": "example_food", "unit": "example_unit", "gram": 100, '
            '"Calories": 100, "Carbohydrates": 100, '
            '"Protein": 100, "Fat": 100}].\n'
            "Please respond only as a valid JSON array, without any additional text or description."
            "Make sure the values are realistic and accurately reflect the nutritional content of each food item."
        )

        gpt_response = rag_instance.generate_response_with_rag(prompt, food_names, gpt_api_key)

        # 백틱을 제거하고 JSON 파싱 시도
        gpt_response_cleaned = gpt_response.replace("```json", "").replace("```", "").strip()
        try:
            gpt_response_json = json.loads(gpt_response_cleaned)
            response_json = json.dumps({"data": gpt_response_json}, ensure_ascii=False, indent=4)
            logger.info(f"Received response from OpenAI: {gpt_response}")
            return Response(response_json, mimetype='application/json')
        except json.JSONDecodeError:
            logger.error("Error converting response to JSON: No JSON object found in GPT response")
            return jsonify({
                "error": "Invalid JSON response from OpenAI",
                "gpt_response": gpt_response_cleaned
            }), 500

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500
