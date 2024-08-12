import openai
import logging
from app.models.GPT.init import get_gpt_model

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_response(prompt, api_key, max_tokens=1000, temperature=0.9):
    """
    GPT 모델을 사용하여 프롬프트에 대한 응답을 생성합니다.
    헤더로 전달받은 API 키를 사용하며, 동적으로 모델을 설정합니다.
    """
    try:
        # OpenAI API 키 설정
        openai.api_key = api_key

        # GPT 모델에 프롬프트를 전달하고 응답 생성
        response = openai.ChatCompletion.create(
            model = get_gpt_model(),
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        gpt_response = response.choices[0].message['content'].strip()
        return gpt_response
    except openai.error.AuthenticationError:
        logger.error("Invalid API key provided for OpenAI.")
        return "Authentication failed: Invalid API key."
    except Exception as e:
        logger.error(f"Error in generating response: {e}")
        return f"An error occurred: {str(e)}"
