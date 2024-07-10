import os
from dotenv import load_dotenv

# .env 파일의 환경 변수를 로드
load_dotenv()


# 환경 변수에 있는 키 값 불러 오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
