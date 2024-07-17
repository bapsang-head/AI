from flask import Blueprint, request, jsonify
from app.services.ner_service import ner_model
from app.services.gpt_service import generate_response

first_GPT_API_blueprint = Blueprint('diet', __name__)

@first_GPT_API_blueprint.route('/', methods=['POST'])
def process_diet():
    data = request.json
    
    # NER 모델을 사용하여 입력 데이터 처리
    ner_result = ner_model(data["user_input"])
    
    # NER 결과를 기반으로 GPT에 데이터 전송
    ner_result_str = ", ".join([f'{{"index": {item["index"]}, "word": "{item["word"]}", "tag": "{item["tag"]}"}}' for item in ner_result])
    prompt = (
        f'Input: {data["user_input"]}\n'
        f'NER Output: [{ner_result_str}]\n'
        'Refer to NER Output to output the food, quantity, and unit in the text of the input data in JSON format. '
        'If any information is missing, tag it as "Null".'
    )
    gpt_response = generate_response(prompt)
    
    return jsonify({"data": gpt_response})
