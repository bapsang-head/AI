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
    user_input = "나는 오늘 삼겹살을 1인분을 먹었고, 후식으로 딸기는 3개를 먹었어, 그리고 한잔 했어"
    
    # NER 모델을 사용하여 입력 데이터 처리
    ner_result = ner_model(user_input)
    
    # NER 결과를 기반으로 GPT에 데이터 전송
    ner_result_str = ", ".join([f'{{""word": "{item["word"]}", "tag": "{item["tag"]}"}}' for item in ner_result])
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
    
    # JSON 응답 보기 좋게 출력
    print("GPT 응답:")
    try:
        response_json = json.loads(gpt_response)
        print(json.dumps(response_json, indent=4, ensure_ascii=False))
    except json.JSONDecodeError:
        print(gpt_response)
