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
        # 요청 헤더에서 키 가져오기
        header_key = request.headers.get('ACTIVATE_KEY')

        # 문자열 비교 전에 공백 제거 및 대소문자 무시 처리
        if not header_key or header_key.strip().lower() != activate_key.strip().lower():
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

        # 프롬프트 1: 각 음식의 단위를 gram으로 변환
        prompt_gram = (
            f"다음은 음식과 단위의 목록입니다: {json.dumps(food_items, ensure_ascii=False, indent=4)}.\n"
            "각 음식의 단위를 gram으로 변환하세요.\n"
            "JSON 형식으로 반환해 주세요:\n"
            '[{"food": "예시_음식", "unit": "예시_단위", "gram": 100}].\n'
            "추가적인 텍스트나 설명 없이, 유효한 JSON 배열로만 응답해 주세요."
        )

        gpt_response_gram = generate_response(prompt_gram)

        # 불필요한 줄바꿈이나 공백 제거
        gpt_response_gram = gpt_response_gram.replace('\n', '').replace('\r', '').replace(' ', '')
        logger.info("GPT response to gram:\n%s \n", gpt_response_gram)

        # 음식 이름만 추출하여 리스트 생성
        gram_data = json.loads(gpt_response_gram)
        food_names = [item['food'] for item in gram_data]

        # RAG를 사용해 각 음식의 영양 정보를 검색
        all_nutrition_info = []
        for food_name in food_names:
            nutrition_info = rag_instance.search_nutrition_info(food_name)
            if nutrition_info:
                # 각 항목 사이에 줄바꿈과 공백 추가
                cleaned_nutrition_info = [info.replace('\t', ' ').replace('\n', ' ').replace('\r', '').strip() for info in nutrition_info]
                formatted_info = "\n".join(cleaned_nutrition_info)
                all_nutrition_info.append(f"{food_name}: {formatted_info}")
        
        logger.info("All nutrition result:\n%s", "\n\n".join(all_nutrition_info))

        # 프롬프트 2: 100g 기준으로 영양 성분 계산
        prompt_nutrition = (
            f"다음은 음식 목록입니다: {json.dumps(food_names, ensure_ascii=False, indent=4)}.\n"
            "다음은 우리의 데이터베이스에서 검색된 다음 영양 정보를 참고하세요:\n" +
            "\n".join(all_nutrition_info) + "\n"
            "각 음식의 영양 정보를 100g 기준으로 계산하세요.\n"
            "JSON 형식으로 반환해 주세요:\n"
            '[{"food": "예시_음식", "Calories": 100, "Carbohydrates": 100, "Protein": 100, "Fat": 100}].\n'
            "추가적인 텍스트나 설명 없이, 유효한 JSON 배열로만 응답해 주세요."
        )

        gpt_response_nutrition = generate_response(prompt_nutrition)

        # 불필요한 줄바꿈이나 공백 제거
        gpt_response_nutrition = gpt_response_nutrition.replace('\n', '').replace('\r', '').replace(' ', '')
        logger.info("\nGPT response to nutrition:\n%s", gpt_response_nutrition)

        # JSON 파싱 및 병합
        try:
            nutrition_data = json.loads(gpt_response_nutrition)

            # 병합된 결과 생성
            combined_data = []
            for i, gram_item in enumerate(gram_data):
                food_name = gram_item["food"]
                unit_name = food_items[i]["unit"]  # 올바르게 unit 값을 가져옴
                matching_nutrition = next((item for item in nutrition_data if item["food"] == food_name), None)
                if matching_nutrition:
                    combined_entry = {
                        "food": food_name,
                        "unit": unit_name,
                        "gram": gram_item["gram"],
                        "Calories": matching_nutrition["Calories"],
                        "Carbohydrates": matching_nutrition["Carbohydrates"],
                        "Protein": matching_nutrition["Protein"],
                        "Fat": matching_nutrition["Fat"],
                    }
                    combined_data.append(combined_entry)

            response_json = json.dumps({"data": combined_data}, ensure_ascii=False, indent=4)
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
