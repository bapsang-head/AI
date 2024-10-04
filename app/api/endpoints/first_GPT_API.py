from flask import Flask, Blueprint, request, jsonify, Response
from app.services.ner_service import ner_model
from app.services.gpt_service import generate_response
from app.services.rate_limiter import RateLimiter 
from dotenv import load_dotenv
import os
import json
import logging

app = Flask(__name__)
first_GPT_API_blueprint = Blueprint('first_GPT_API', __name__)

logging.basicConfig(level=logging.INFO)

# .env 파일에서 환경 변수 로드
load_dotenv()
activate_key = os.getenv("ACTIVATE_KEY")
call_initialization_key = os.getenv("CALL_INITIALIZATION")  # 추가

# 하루에 최대 500회로 API 호출 제한을 초기화
rate_limiter = RateLimiter(max_calls=500, call_initialization_key=call_initialization_key)

@first_GPT_API_blueprint.route('/', methods=['POST'])
@rate_limiter.limit_api_calls  # 데코레이터 적용
def process_NER():
    try:
        # 호출 초기화를 위한 헤더에서 키 가져오기
        init_key = request.headers.get('CALL_INITIALIZATION')

        # 호출 초기화 키 확인
        if init_key and init_key.strip() == call_initialization_key.strip():
            rate_limiter.reset_calls()  # 호출 횟수 초기화
            return jsonify({"message": "API call count has been reset"}), 200

        # 기존 키 확인 로직
        header_key = request.headers.get('ACTIVATE_KEY')

        # 문자열 비교 전에 공백 제거 및 대소문자 무시 처리
        if not header_key or header_key.strip().lower() != activate_key.strip().lower():
            return jsonify({"error": "Invalid or missing activation key in headers"}), 403

        # API 호출 로직 (이 부분에서 호출 횟수 카운트가 이루어짐)
        data = request.get_json(force=True)
        if not data or 'user_input' not in data:
            logging.error("Invalid input: %s", data)
            return jsonify({"error": "Invalid input"}), 400

        user_input = data['user_input']

        # NER 모델을 사용하여 입력 데이터 처리
        ner_result = ner_model(user_input)
        logging.info("NER result: %s", ner_result)

        prompt = (
            f'입력 텍스트는 다음과 같습니다: "{user_input}".\n'
            f'NER 출력 결과는 다음과 같습니다: [{ner_result}].\n'
            '텍스트의 문맥을 고려하여 누락된 음식 항목, 수량 및 단위를 식별하세요. '
            '다음 규칙을 적용하여 추가 개체명 인식을 수행하세요:\n'
            '1. 문맥을 고려해서 개체명 인식을 수행해줘 예를 들면 "국수를 비벼"라는 표현은 "비빔국수"로 인식하고, "밥을 볶아"라는 표현은 "볶음밥"으로 인식하세요.\n'
            '2. 수량(quantity)은 반드시 숫자(int) 형태로 반환하세요. 예를 들어, "한 개"는 1, "두 개"는 2와 같이 숫자로 변환합니다.\n'
            '결과를 JSON 형식으로 반환하며, 각 음식 항목, 수량 및 단위가 적절히 태그된 형식을 사용하세요. '
            '정보가 누락된 경우에는 "null"(소문자)로 명시하세요. '
            'quantity가 null인 경우는 숫자(int)로 1로 반환하도록 한다.'
            '하지만 food, quantity, unit이 전부 null인 경우는 없으니 결과로 전부 null이 나오면 생략해서 답변을 주세요.\n'
            'JSON 형식은 다음과 같아야 합니다: '
            '[{"food": "예시_음식", "quantity": 숫자_수량(int), "unit": "예시_단위"}]. '
            '모든 텍스트와 태그는 한국어로 반환하세요. 추가적인 설명이나 텍스트는 포함하지 마세요.'
        )


        gpt_response = generate_response(prompt)
        logging.info("GPT response: %s", gpt_response)

        # 백틱을 제거하고 JSON 파싱 시도
        gpt_response_cleaned = gpt_response.replace("```json", "").replace("```", "").strip()
        try:
            gpt_response_json = json.loads(gpt_response_cleaned)
        except json.JSONDecodeError:
            logging.error("Failed to decode GPT response as JSON: %s", gpt_response_cleaned)
            return jsonify({"error": "Invalid JSON response from OpenAI", "gpt_response": gpt_response_cleaned}), 500

        response_json = json.dumps({"data": gpt_response_json}, ensure_ascii=False, indent=4)
        return Response(response_json, mimetype='application/json')

    except Exception as e:
        logging.error("Error processing request: %s", e)
        return jsonify({"error": "Internal server error"}), 500

app.register_blueprint(first_GPT_API_blueprint, url_prefix='/first_GPT_API')

if __name__ == "__main__":
    app.run(port=5001)
