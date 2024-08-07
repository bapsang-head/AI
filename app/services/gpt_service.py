import openai
import logging
from app.config import Config

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
        # logger.info(f"Sending prompt to OpenAI: {prompt}")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        gpt_response = response.choices[0].message['content'].strip()
        # logger.info(f"Received response from OpenAI: {gpt_response}")
        return gpt_response
    except Exception as e:
        logger.error(f"Error in generating response: {e}")
        return ""