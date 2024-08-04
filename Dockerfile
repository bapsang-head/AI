# Python 3.9 기반의 도커 이미지 사용
FROM python:3.9

# Python 인코딩으로 utf-8 사용
ENV PYTHONIOENCODING=utf-8

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 현재 디렉토리의 모든 내용을 컨테이너의 /app에 복사
COPY . .

# requirements.txt에 명시된 필요한 패키지들을 설치
RUN pip install --upgrade pip
RUN pip install flask
RUN pip install --no-cache-dir -r requirements.txt

# 외부에서 이 컨테이너의 5000 포트를 사용할 수 있도록 설정
EXPOSE 5000

# 환경 변수 정의
ENV FLASK_APP=app.main
ENV FLASK_ENV=development

# flask 명령어 실행
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=5001"]
