from flask import Blueprint, request, jsonify, Response
from app.services.gpt_service import generate_response
import json
import logging

logger = logging.getLogger(__name__)

second_GPT_API_blueprint = Blueprint('second_GPT_API', __name__)

@second_GPT_API_blueprint.route('/', methods=['POST'])
def process_second_GPT_API():
    data = request.json

    logger.info(f"Received data: {data}")

    food_items = []
    for i in range(0, len(data["data"]), 2):
        food_items.append({
            "food": data["data"][i]["word"],
            "unit": data["data"][i + 1]["word"]
        })

    prompt = (
        f'The following is a list of foods and their units: {food_items}.\n'
        'For each food item, convert the unit to grams and provide the nutritional information per 100g. '
        'However, keep the original unit in the JSON output as provided in the input. '
        'Return the results in JSON format with each food item and its corresponding nutritional values. '
        'The JSON format should look like this: '
        '[{"food": "example_food", "unit": "example_unit", "gram": 100, '
        '"calories": 100, "carbohydrates": 100, '
        '"protein": 100, "fat": 100}]. '
        'Respond only with a valid JSON array. Do not include any additional text or explanation. '
        'The values should be realistic and accurate based on the food items.'
    )

    gpt_response = generate_response(prompt)

    try:
        gpt_response_json = json.loads(gpt_response)
        response_json = json.dumps({"data": gpt_response_json}, ensure_ascii=False, indent=4)
        logger.info(f"Received response from OpenAI: {gpt_response}")
        return Response(response_json, mimetype='application/json')
    except json.JSONDecodeError:
        logger.error("Error converting response to JSON: No JSON object found in GPT response")
        return jsonify({
            "error": "Invalid JSON response from OpenAI",
            "gpt_response": gpt_response
        }), 500
