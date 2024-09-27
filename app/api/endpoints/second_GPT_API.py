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
call_initialization_key = os.getenv("CALL_INITIALIZATION")

# 하루에 최대 500회로 API 호출 제한을 초기화
rate_limiter = RateLimiter(max_calls=500, call_initialization_key=call_initialization_key)

@second_GPT_API_blueprint.route('/', methods=['POST'])
@rate_limiter.limit_api_calls  # 데코레이터 적용
def process_second_GPT_API():
    try:
        header_key = request.headers.get('ACTIVATE_KEY')

        # 문자열 비교 전에 공백 제거 및 대소문자 무시 처리
        if not header_key or header_key.strip().lower() != activate_key.strip().lower():
            return jsonify({"error": "Invalid or missing activation key in headers"}), 403

        data = request.json
        if not data or 'food' not in data or 'unit' not in data:
            logger.error("Invalid input or empty data: %s", data)
            return jsonify({"error": "Invalid input or empty data"}), 400

        logger.info(f"Received data: {json.dumps(data, ensure_ascii=False, indent=4)}")

        # 단일 음식 처리
        food_item = {
            "food": data["food"],
            "unit": data["unit"]
        }

        # 프롬프트 1: 음식을 gram으로 변환
        prompt_gram = (
            f"음식과 단위는 다음과 같습니다: {json.dumps(food_item, ensure_ascii=False)}.\n"
            "이 음식의 단위를 gram으로 변환하고 정확한 JSON 형식으로 반환하세요.\n"
            '형식: {"food": "음식이름", "unit": "단위", "gram": 100}.\n'
            "추가 설명 없이 유효한 JSON만 반환하세요."
        )

        gpt_response_gram = generate_response(prompt_gram)

        # 백틱과 불필요한 줄바꿈, 공백 제거
        gpt_response_gram = gpt_response_gram.replace('```json', '').replace('```', '').strip()

        # 응답에서 정확한 JSON 부분만 추출하는 방법
        try:
            start_index = gpt_response_gram.find('{')
            end_index = gpt_response_gram.rfind('}') + 1
            gpt_response_gram = gpt_response_gram[start_index:end_index]

            # JSON 파싱
            gram_data = json.loads(gpt_response_gram)
            if not isinstance(gram_data, dict) or not gram_data:
                logger.error("Parsed gram_data is not a valid dict: %s", gram_data)
                return jsonify({"error": "Invalid gram data format"}), 500
        except json.JSONDecodeError as e:
            logger.error("Error decoding GPT gram response: %s", e)
            return jsonify({"error": "Invalid JSON in GPT gram response", "gpt_response_gram": gpt_response_gram}), 500

        # RAG를 사용해 음식의 영양 정보를 검색
        food_name = gram_data['food']
        nutrition_info = rag_instance.search_nutrition_info(food_name)

        if nutrition_info:
            # 각 항목에 \n 추가 후 결합
            cleaned_nutrition_info = [info.replace('\t', ' ').replace('\n', ' ').replace('\r', '').strip() + '\n' for info in nutrition_info]
            formatted_info = "".join(cleaned_nutrition_info)
        else:
            logger.warning(f"No nutrition info found for {food_name}")
            return jsonify({"error": "No nutrition info found for food"}), 404

        logger.info(f"rag info data: \n {formatted_info}")

        # 프롬프트 2: 100g 기준으로 영양 성분 계산
        prompt_nutrition = (
            f"음식: {food_name}.\n"
            "이 음식의 영양 정보를 100g 기준으로 계산하고 정확한 JSON 형식으로 반환하세요.\n"
            '형식: {"food": "음식이름", "Calories": 100, "Carbohydrates": 100, "Protein": 100, "Fat": 100}.\n'
            "다음은 현재 최신 데이터 베이스에서 찾은 음식 영양 성분 데이터 입니다. 이를 참고하여 작성해주세요."
            f"데이터 : {formatted_info}\n"
            "추가 설명 없이 유효한 JSON만 반환하세요."
        )

        gpt_response_nutrition = generate_response(prompt_nutrition)

        # 백틱과 불필요한 줄바꿈, 공백 제거
        gpt_response_nutrition = gpt_response_nutrition.replace('```json', '').replace('```', '').replace('\n', '').replace('\r', '').strip()

        # JSON 파싱 및 최종 병합
        try:
            start_index = gpt_response_nutrition.find('{')
            end_index = gpt_response_nutrition.rfind('}') + 1
            gpt_response_nutrition = gpt_response_nutrition[start_index:end_index]

            nutrition_data = json.loads(gpt_response_nutrition)
            if not isinstance(nutrition_data, dict) or not nutrition_data:
                logger.error("Parsed nutrition_data is not a valid dict: %s", nutrition_data)
                return jsonify({"error": "Invalid nutrition data format"}), 500

            # 문자열을 float 타입으로 변환
            try:
                gram = float(gram_data.get('gram', '0'))
                calories = float(nutrition_data.get('Calories', '0'))
                carbohydrates = float(nutrition_data.get('Carbohydrates', '0'))
                protein = float(nutrition_data.get('Protein', '0'))
                fat = float(nutrition_data.get('Fat', '0'))
            except ValueError as e:
                logger.error("Error converting string to float: %s", e)
                return jsonify({"error": "Invalid number format"}), 500

            # 병합된 결과 생성
            combined_entry = {
                "food": gram_data["food"],
                "unit": food_item["unit"],
                "gram": gram,
                "calories": calories,
                "carbohydrates": carbohydrates,
                "protein": protein,
                "fat": fat,
            }

            response_json = json.dumps(combined_entry, ensure_ascii=False, indent=4)
            logger.info(f"Final combined response: \n{response_json}")
            return Response(response_json, mimetype='application/json')

        except json.JSONDecodeError as e:
            logger.error("Error converting response to JSON: %s", str(e))
            return jsonify({
                "error": "Invalid JSON response from OpenAI",
                "gpt_response_gram": gpt_response_gram,
                "gpt_response_nutrition": gpt_response_nutrition
            }), 500

    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error"}), 500
