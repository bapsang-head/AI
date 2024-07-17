from flask import Blueprint, request, jsonify
from app.services.gpt_service import generate_response

second_GPT_API_blueprint = Blueprint('result', __name__)

@second_GPT_API_blueprint.route('/', methods=['POST'])
def process_result():
    data = request.json
    
    # 음식 및 단위 정보를 기반으로 프롬프트 생성
    food_data = data["data"]
    food_items = []

    # 음식과 단위가 교대로 나오므로, 이를 매칭하여 food_items에 추가
    for i in range(0, len(food_data), 2):
        food_items.append({
            "food": food_data[i]["word"],
            "unit": food_data[i + 1]["word"]
        })

    prompt = (
        f'The following is a list of foods and their units: {food_items}.\n'
        'For each food item, convert the unit to grams and provide the nutritional information per 100g. '
        'Return the results in JSON format with each food item and its corresponding nutritional values. '
        'The JSON format should look like this: '
        '[{"food": "example_food", "unit": "example_unit", "gram": "example_gram", "calories": "example_calories", '
        '"carbohydrates": "example_carbohydrates", "protein": "example_protein", "fat": "example_fat"}]. '
        'Do not include any additional text, only return the JSON.'
    )

    gpt_response = generate_response(prompt)

    return jsonify({"data": gpt_response})
