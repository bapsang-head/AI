# AI

노션에 올린 API 명세서 기준으로 구성한 구조이다

## 환경 변수 설정
이 프로젝트는 환경 변수를 사용합니다.  
`.env` 파일을 프로젝트 루트 디렉토리에 생성하고 gpt 키값을 추가해야 정상적으로 동작합니다.

### 현재 진행 상황 (2024.07.16 기준)
- Dockerfile을 공부중
    - 간단하게 Dockerfile 만들어보긴 함
- 현재 GPT 호출 부분 전체적인 수정 들어갈 예정
- GPT API 호출해서 통신하는 부분 끝나면 RAG 기술 넣을 예정

### 첫번째 GPT 호출
#### 1. 입력
- 개체명 인식을 하고 태깅된 문장을 GPT를 통해 예외케이스까지 잡아는 형식으로 진행한다
    ```json
    {
        "user_input": "나는 점심에 삽겹살을 2 인분과 소주을 먹었어. 밥도 3공기 볶아 먹었어",
        "data": [
            {"index": 1, "word": "삽겹살", "tag": "B-FOOD"},
            {"index": 2, "word": "2", "tag": "B-QTY"},
            {"index": 3, "word": "인분", "tag": "B-UNIT"},
            {"index": 4, "word": "소주", "tag": "B-FOOD"},
            {"index": 5, "word": "밥", "tag": "B-FOOD"},
            {"index": 6, "word": "3", "tag": "B-QTY"},
            {"index": 7, "word": "공기", "tag": "B-UNIT"}
        ]
    }
    ``` 
#### 2. 응답
- NER 모델이 잡아내지 못한 부분까지 잡아내는 응답을 만들어낸다.
    ```json
    {
        "data": [
            {"index": 1, "word": "삽겹살", "tag": "B-FOOD"},
            {"index": 2, "word": "2", "tag": "B-QTY"},
            {"index": 3, "word": "인분", "tag": "B-UNIT"},
            {"index": 4, "word": "소주", "tag": "B-FOOD"},
            {"index": 5, "word": "Null", "tag": "B-QTY"},
            {"index": 6, "word": "Null", "tag": "B-UNIT"},
            {"index": 7, "word": "볶음밥", "tag": "B-FOOD"},
            {"index": 8, "word": "3", "tag": "B-QTY"},
            {"index": 9, "word": "공기", "tag": "B-UNIT"}
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
    {
        "data": [
            {"index": 1, "word": "삽겹살", "tag": "B-FOOD"},
            {"index": 2, "word": "인분", "tag": "B-UNIT"},
            {"index": 3, "word": "200", "tag": "gram"},
            {"index": 4, "word": "200", "tag": "calories"},
            {"index": 5, "word": "50", "tag": "carbohydrates"},
            {"index": 6, "word": "20", "tag": "protein"},
            {"index": 7, "word": "10", "tag": "fat"},
            {"index": 8, "word": "볶음밥", "tag": "B-FOOD"},
            {"index": 9, "word": "공기", "tag": "B-UNIT"},
            {"index": 10, "word": "150", "tag": "gram"},
            {"index": 11, "word": "200", "tag": "calories"},
            {"index": 12, "word": "50", "tag": "carbohydrates"},
            {"index": 13, "word": "100", "tag": "protein"},
            {"index": 14, "word": "20", "tag": "fat"},
        ]
    }
    ``` 