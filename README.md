# AI

태진형이 올린 API 명세서 기준으로 구성한 구조이다

project_root/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── endpoints/
│   │   │   ├── __init__.py
│   │   │   ├── diet.py  # 자연어 입력 엔드포인트
│   │   │   └── result.py  # 처리 결과 엔드포인트
│   │   └── schemas/
│   │       ├── __init__.py
│   │       ├── diet_schema.py  # 요청/응답 스키마
│   │       └── result_schema.py  # 결과 스키마
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ner_service.py  # NER 서비스 로직
│   │   └── gpt_service.py  # GPT 서비스 로직
│   ├── db/
│   │   ├── __init__.py
│   │   ├── models.py  # 데이터베이스 모델 정의
│   │   └── session.py  # 데이터베이스 세션 관리
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── data_processing.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_generalizing/
│   │   │   ├── __init__.py
│   │   │   ├── data_generizing.py
│   │   │   ...
│   │   ├── data.tsv
│   ├── models/
│   │   ├── KoBERT-NER/
│   │   │   ├── __init__.py
│   │   │   ├── trainer.py
│   │   │   ...
│   │   ├── GPT4o/
│   │   │   ├── __init__.py
│   │   │   ...
├── tests/
│   ├── __init__.py
│   ├── test_ner_service.py
│   ├── test_gpt_service.py
├── .env
├── requirements.txt
├── README.md
