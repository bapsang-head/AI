import openai
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

def generate_response(prompt, max_tokens=300, temperature=0.7):
    """
    GPT 모델을 사용하여 프롬프트에 대한 응답을 생성합니다.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            # model = "gpt-4o",
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
