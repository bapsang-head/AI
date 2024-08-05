# AI

### 현재 진행 상황 (2024.08.05 기준)
- RAG 기술은 좀 더 공부하고 넣을 예정
- GPT API 호출 결과에서 여러가지의 오류들을 시도 해보기
- endpoint에서 출력 형식 다시 맞추기 (README 처럼 만들기) *

## 환경 변수 설정
이 프로젝트는 환경 변수를 사용합니다.  
`.env` 파일을 프로젝트 루트 디렉토리에 생성하고 gpt 키값을 추가해야 정상적으로 동작합니다.

### GPT model은 GPT 4o로 통일

### kobert
- 유저 raw 입력 문장을 ko-bert를 통해 인식한 개체명들을 출력하는 함수는 app/service/ner_service.py에 있는 ner_model 함수이다.
- 여기서 출력하는 내용은 하단에 있는 첫번째 GPT 호출의 입력과 동일하다.


### 첫번째 GPT 호출
#### 1. 입력
- 개체명 인식을 하고 태깅된 문장을 GPT를 통해 예외케이스까지 잡아는 형식으로 진행한다
    ```json
    {
        "user_input": "나는 점심으로 삽결살 1인분과 소주 한잔을 먹었어",
        "data": [
                {"word": "삽결살 ", "tag": "B-FOOD"},
                {"word": "1", "tag": "B-QTY"},
                {"word": "인분", "tag": "B-UNIT"},
                {"word": "소주", "tag": "B-FOOD"},
                {"word": "한", "tag": "B-QTY"},
                {"word": "잔", "tag": "B-UNIT"}
        ]
    }
    ``` 
#### 2. 응답
- NER 모델이 잡아내지 못한 부분까지 잡아내는 응답을 만들어낸다.
    ```json
    { 
        "data":[
            {"food": "삼겹살", "quantity": "1", "unit": "인분"},
            {"food": "소주", "quantity": "한", "unit": "잔"}
        ]
    }
    ```
### 두번째 GPT 호출
#### 1. 입력
- 음식, 단위 정보가 DB에 없는 경우 호출하는 경우이다.
- 무조건 음식명과 단위를 전부 넘겨줘야 한다.
    ```json
    {
        "data": [
            {"index": 1, "word": "삽겹살", "tag": "B-FOOD"},
            {"index": 2, "word": "인분", "tag": "B-UNIT"},
            {"index": 3, "word": "볶음밥", "tag": "B-FOOD"},
            {"index": 4, "word": "공기", "tag": "B-UNIT"},
        ]
    }
    ``` 
#### 2. 응답
- 단위당 g으로 변환된 값과 영양정보를 응답으로 보여준다. 
- 영양정보는 100g을 기준으로 보여준다. (칼로리, 탄수화물, 단백질, 지방)
- 한 음식당 7개의 정보를 가지고 온다.
    ```json
        [
            {
                "food": "삽겹살",
                "unit": "인분",
                "gram": 200,
                "calories": 520,
                "carbohydrates": 0,
                "protein": 21.7,
                "fat": 47.5
            },
            {
                "food": "볶음밥",
                "unit": "공기",
                "gram": 250,
                "calories": 220,
                "carbohydrates": 28,
                "protein": 4.8,
                "fat": 10
            }
        ]
    ``` 