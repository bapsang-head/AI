from flask import Flask, Blueprint, request, jsonify, Response
from app.services.ner_service import ner_model
from app.services.gpt_service import generate_response
import json
import logging

app = Flask(__name__)

first_GPT_API_blueprint = Blueprint('diet', __name__)

@first_GPT_API_blueprint.route('/', methods=['POST'])
def process_NER():
    try:
        data = request.json
        # logging.info(f"Received data: {data}")
        
        # NER 모델을 사용하여 입력 데이터 처리
        ner_result = ner_model(data["user_input"])
        # logging.info(f"NER result: {ner_result}")
        
        # ner_result가 None인 경우 빈 리스트로 초기화
        if ner_result is None:
            logging.error("ner_model returned None")
            ner_result = []
        
        # NER 결과를 기반으로 GPT에 데이터 전송
        ner_result_str = ", ".join([f'{{"word": "{item["word"]}", "tag": "{item["tag"]}"}}' for item in ner_result])
        prompt = (
            f'The input text is: "{data["user_input"]}".\n'
            f'The NER output is: [{ner_result_str}].\n'
            'Please identify any missing food items, quantities, and units in the input text. '
            'Return only the results in JSON format with each food item, quantity, and unit properly tagged. '
            'If any information is missing, explicitly use "null" (in lowercase) instead of leaving it blank. '
            'The JSON format should look like this: '
            '[{"food": "example_food", "quantity": "example_quantity", "unit": "example_unit"}].'
        )
        gpt_response = generate_response(prompt)
        
        # gpt_response가 빈 문자열인 경우 처리
        if not gpt_response:
            logging.error("generate_response returned an empty response")
            raise ValueError("GPT response is empty")
        
        # logging.info(f"GPT response: {gpt_response}")
        
        # GPT 응답을 JSON 형식으로 변환
        gpt_response_json = json.loads(gpt_response)
        
        # JSON 데이터를 문자열로 변환하면서 실제 줄바꿈 문자 포함
        response_json = json.dumps({"data": gpt_response_json}, ensure_ascii=False, indent=4)
        
        # Response 객체로 반환하여 Content-Type을 application/json으로 설정
        return Response(response_json, mimetype='application/json')
    
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        response = {"error": str(e)}
        return jsonify(response), 500

app.register_blueprint(first_GPT_API_blueprint, url_prefix='/first_GPT_API')
