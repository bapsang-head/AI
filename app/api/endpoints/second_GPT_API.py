from flask import Blueprint, request, jsonify, Response
from app.services.gpt_service import generate_response
from app.services.rate_limiter import RateLimiter 
from app.models.RAG.rag import RAG
from dotenv import load_dotenv
import os
import json
import logging

logger = logging.getLogger(__name__)
rag_instance = RAG()

second_GPT_API_blueprint = Blueprint('second_GPT_API', __name__)

# .env 파일에서 환경 변수 로드
load_dotenv()
activate_key = os.getenv("ACTIVATE_KEY")

# 하루에 최대 10회로 API 호출 제한을 초기화
rate_limiter = RateLimiter(max_calls=10)

@second_GPT_API_blueprint.route('/', methods=['POST'])
@rate_limiter.limit_api_calls  # API 호출 제한 데코레이터 적용
def process_second_GPT_API():
    try:
        logger.info(f"Received request: {request.data.decode('utf-8')}")

        # 요청 헤더에서 키 가져오기
        header_key = request.headers.get('ACTIVATE-KEY')
        if not header_key or header_key != activate_key:
            return jsonify({"error": "Invalid or missing activation key in headers"}), 403

        data = request.json
        if not data or 'data' not in data:
            logger.error("Invalid input: %s", data)
            return jsonify({"error": "Invalid input"}), 400

        logger.info(f"Received data: {json.dumps(data, ensure_ascii=False, indent=4)}")

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
                # 각 항목 사이에 줄바꿈과 공백 추가
                cleaned_nutrition_info = [info.replace('\t', ' ').replace('\n', ' ').replace('\r', '').strip() for info in nutrition_info]
                formatted_info = "\n".join(cleaned_nutrition_info)
                all_nutrition_info.append(formatted_info)

        # 로그 출력 시 각 항목을 명시적으로 구분
        logger.info("All nutrition result:\n%s", "\n\n".join(all_nutrition_info))

        # 프롬프트 설정
        prompt = (
            f"Here is a list of foods and their units: {json.dumps(food_items, ensure_ascii=False, indent=4)}.\n"
            "For each food, the unit is converted to grams and provided in a category called gram. Additionally, nutritional information is provided per 100g."
            "The original units should be preserved in the JSON output, reflecting the input format."
            "Additionally, use the following nutritional information retrieved from our database:\n"
            + "\n\n".join(all_nutrition_info) + "\n"
            "Returns results strictly in JSON format:\n"
            '[{"food": "example_food", "unit": "example_unit", "gram": 100, '
            '"Calories": 100, "Carbohydrates": 100, '
            '"Protein": 100, "Fat": 100}].\n'
            "Please respond only as a valid JSON array, without any additional text or description."
            "Make sure the values are realistic and accurately reflect the nutritional content of each food item."
        )

        gpt_response = generate_response(prompt)  # API 키를 더 이상 전달하지 않음

        # 백틱을 제거하고 JSON 파싱 시도
        gpt_response_cleaned = gpt_response.replace("```json", "").replace("```", "").strip()
        try:
            gpt_response_json = json.loads(gpt_response_cleaned)
            response_json = json.dumps({"data": gpt_response_json}, ensure_ascii=False, indent=4)
            logger.info(f"Received response from OpenAI: \n{response_json}")
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
