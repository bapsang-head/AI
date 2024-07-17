import openai
import logging
import json
from app.config import Config
from app.services.ner_service import ner_model

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OpenAI API 키 설정
openai.api_key = Config.OPENAI_API_KEY

def generate_response(prompt, max_tokens=200, temperature=0.9):
    """
    GPT 모델을 사용하여 프롬프트에 대한 응답을 생성합니다.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        logger.error(f"Error in generating response: {e}")
        return str(e)

if __name__ == "__main__":
    # 테스트 프롬프트
    food_data = [
        {"word": "삽겹살", "tag": "B-FOOD"},
        {"word": "인분", "tag": "B-UNIT"},
        {"word": "볶음밥", "tag": "B-FOOD"},
        {"word": "공기", "tag": "B-UNIT"},
    ]

    # 음식과 단위를 매칭하여 food_items에 추가
    food_items = []
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
    
    # JSON 응답 보기 좋게 출력
    print("GPT 응답:")
    try:
        response_json = json.loads(gpt_response)
        print(json.dumps(response_json, indent=4, ensure_ascii=False))
    except json.JSONDecodeError:
        print(gpt_response)
