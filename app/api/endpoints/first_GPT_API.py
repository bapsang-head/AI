from flask import Flask, Blueprint, request, jsonify, Response
from app.services.ner_service import ner_model
from app.services.gpt_service import generate_response
from app.services.rate_limiter import RateLimiter
import json
import logging
import re

app = Flask(__name__)
first_GPT_API_blueprint = Blueprint('first_GPT_API', __name__)

logging.basicConfig(level=logging.INFO)

# 하루에 최대 100회로 API 호출 제한을 초기화
rate_limiter = RateLimiter(max_calls=100)

@first_GPT_API_blueprint.route('/', methods=['POST'])
@rate_limiter.limit_api_calls
def process_NER():
    """
    NER (Named Entity Recognition) 처리를 수행하는 API 엔드포인트.
    하루에 100회까지 호출이 가능하며, 그 이상 호출 시 429 에러를 반환합니다.
    """
    try:
        logging.info("Received request: %s", request.data)
        
        data = request.get_json(force=True)
        if not data or 'user_input' not in data:
            logging.error("Invalid input: %s", data)
            return jsonify({"error": "Invalid input"}), 400
        
        user_input = data['user_input']
        logging.info("Received user input: %s", user_input)
        
        # NER 모델을 사용하여 입력 데이터 처리
        ner_result = ner_model(user_input)
        logging.info("NER result: %s", ner_result)

        # NER 결과를 파싱하여 필요한 정보 추출
        matches = re.findall(r'\[(.+?):(.+?)\]', ner_result)
        ner_result_parsed = [{"word": match[0], "tag": match[1]} for match in matches]
        logging.info("Parsed NER result: %s", ner_result_parsed)

        # GPT에게 전달할 프롬프트 생성
        ner_result_str = ", ".join([f'{{"word": "{item["word"]}", "tag": "{item["tag"]}"}}' for item in ner_result_parsed])
        prompt = (
            f'입력 텍스트는 다음과 같습니다: "{user_input}".\n'
            f'NER 출력 결과는 다음과 같습니다: [{ner_result_str}].\n'
            '텍스트의 문맥을 고려하여 누락된 음식 항목, 수량 및 단위를 식별하세요. '
            '다음 규칙을 적용하여 추가 개체명 인식을 수행하세요:\n'
            '1. 문맥을 고려해서 개체명 인식을 수행해줘 예를 들면 "국수를 비벼"라는 표현은 "비빔국수"로 인식하고, "밥을 볶아"라는 표현은 "볶음밥"으로 인식하세요.\n'
            '결과를 JSON 형식으로 반환하며, 각 음식 항목, 수량 및 단위가 적절히 태그된 형식을 사용하세요. '
            '정보가 누락된 경우에는 "null"(소문자)로 명시하세요. '
            '하지만 food, quantity, unit이 전부 null인 경우는 없으니 결과로 전부 null이 나오면 생략해서 답변을 주세요.' 
            'JSON 형식은 다음과 같아야 합니다: '
            '[{"food": "예시_음식", "quantity": "예시_수량", "unit": "예시_단위"}]. '
            '모든 텍스트와 태그는 한국어로 반환하세요. 추가적인 설명이나 텍스트는 포함하지 마세요.'
        )

        # GPT 모델에 프롬프트 전달하고 결과 수신
        gpt_response = generate_response(prompt)
        logging.info("GPT response: %s", gpt_response)
        
        # 백틱을 제거하고 JSON 파싱 시도
        gpt_response_cleaned = gpt_response.replace("```json", "").replace("```", "").strip()
        try:
            gpt_response_json = json.loads(gpt_response_cleaned)
        except json.JSONDecodeError:
            logging.error("Failed to decode GPT response as JSON: %s", gpt_response_cleaned)
            return jsonify({"error": "Invalid JSON response from OpenAI", "gpt_response": gpt_response_cleaned}), 500
        
        # JSON 응답 반환
        response_json = json.dumps({"data": gpt_response_json}, ensure_ascii=False, indent=4)
        return Response(response_json, mimetype='application/json')
    
    except Exception as e:
        logging.error("Error processing request: %s", e)
        return jsonify({"error": "Internal server error"}), 500

# Blueprint를 등록하여 API를 사용할 수 있도록 설정
app.register_blueprint(first_GPT_API_blueprint, url_prefix='/first_GPT_API')

if __name__ == "__main__":
    app.run(port=5001)
