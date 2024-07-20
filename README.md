# AI

노션에 올린 API 명세서 기준으로 구성한 구조이다

## 환경 변수 설정
이 프로젝트는 환경 변수를 사용합니다.  
`.env` 파일을 프로젝트 루트 디렉토리에 생성하고 gpt 키값을 추가해야 정상적으로 동작합니다.

### 현재 진행 상황 (2024.07.17 기준)
- Dockerfile을 공부중
    - 간단하게 Dockerfile 만들어보긴 함
- RAG 기술은 좀 더 공부하고 넣을 예정
- GPT API 호출 관련한 부분은 작성 완료 (간단한 데이터는 확인 완료)

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
    [
        {
            "food": "삽겹살",
            "quantity": "2",
            "unit": "인분"
        },
        {
            "food": "소주",
            "quantity": null,
            "unit": null
        },
        {
            "food": "밥",
            "quantity": "3",
            "unit": "공기"
        }
    ]
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