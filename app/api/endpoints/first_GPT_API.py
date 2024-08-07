from flask import Flask, Blueprint, request, jsonify, Response
from app.services.ner_service import ner_model
from app.services.gpt_service import generate_response
import json
import logging
import re

app = Flask(__name__)
first_GPT_API_blueprint = Blueprint('first_GPT_API', __name__)

logging.basicConfig(level=logging.INFO)

@first_GPT_API_blueprint.route('/', methods=['POST'])
def process_NER():
    try:
        logging.info("Received request: %s", request.data)  # 요청 데이터 로그 추가
        
        data = request.get_json(force=True)
        if not data or 'user_input' not in data:
            logging.error("Invalid input: %s", data)
            return jsonify({"error": "Invalid input"}), 400
        
        user_input = data['user_input']
        logging.info("Received user input: %s", user_input)
        
        # NER 모델을 사용하여 입력 데이터 처리
        ner_result = ner_model(user_input)
        logging.info("NER result: %s", ner_result)

        # ner_result의 실제 구조를 확인하기 위한 로그 추가
        logging.info("NER result structure: %s", json.dumps(ner_result, ensure_ascii=False))

        # NER 결과를 파싱하여 필요한 정보 추출
        matches = re.findall(r'\[(.+?):(.+?)\]', ner_result)
        ner_result_parsed = [{"word": match[0], "tag": match[1]} for match in matches]
        logging.info("Parsed NER result: %s", ner_result_parsed)

        ner_result_str = ", ".join([f'{{"word": "{item["word"]}", "tag": "{item["tag"]}"}}' for item in ner_result_parsed])
        prompt = (
            f'The input text is: "{user_input}".\n'
            f'The NER output is: [{ner_result_str}].\n'
            'Please identify any missing food items, quantities, and units in the input text. '
            'Return only the results in JSON format with each food item, quantity, and unit properly tagged. '
            'If any information is missing, explicitly use "null" (in lowercase) instead of leaving it blank. '
            'The JSON format should look like this: '
            '[{"food": "example_food", "quantity": "example_quantity", "unit": "example_unit"}].'
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
