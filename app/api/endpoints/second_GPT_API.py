from flask import Blueprint, request, jsonify
from app.services.gpt_service import generate_response

second_GPT_API_blueprint = Blueprint('result', __name__)

@second_GPT_API_blueprint.route('/', methods=['POST'])
def process_result():
    data = request.json
    
    # GPT에 데이터 전송하여 영양 정보 처리
    prompt = (
        f'Input: {data}\n'
        'Please provide the nutritional details per 100g for each item in JSON format, including calories, carbohydrates, protein, and fat.'
    )
    gpt_response = generate_response(prompt)
    
    return jsonify({"data": gpt_response})
