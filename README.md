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
        "user_input": "나는 점심에 김치찌개를 두 그릇과 치킨 세조각을 먹었어",
        "data": [
            {"index": 1, "word": "김치찌개", "tag": "B-FOOD"},
            {"index": 2, "word": "두", "tag": "B-QTY"},
            {"index": 3, "word": "그릇", "tag": "B-UNIT"},
            {"index": 4, "word": "치킨", "tag": "B-FOOD"},
            {"index": 5, "word": "세", "tag": "B-QTY"},
            {"index": 6, "word": "조각", "tag": "B-UNIT"},
        ]
    }
    ``` 

#### 2. 응답
- NER 모델이 잡아내지 못한 부분까지 잡아내는 응답을 만들어낸다.
    ```json
    {
        "user_input": "나는 점심에 김치찌개를 두 그릇과 치킨 세조각을 먹었어",
        "data": [
            {"index": 1, "word": "김치찌개", "tag": "B-FOOD"},
            {"index": 2, "word": "두", "tag": "B-QTY"},
            {"index": 3, "word": "그릇", "tag": "B-UNIT"},
            {"index": 4, "word": "치킨", "tag": "B-FOOD"},
            {"index": 5, "word": "세", "tag": "B-QTY"},
            {"index": 6, "word": "조각", "tag": "B-UNIT"},
        ]
    }
    ``` 

### 두번째 GPT 호출

#### 1. 입력
- 음식, 단위 정보가 DB에 없는 경우 호출하는 경우이다.
    ```json
    {
        "data": [
            {"index": 1, "word": "김치찌개", "tag": "B-FOOD"},
            {"index": 2, "word": "그릇", "tag": "B-UNIT"},
            {"index": 3, "word": "치킨", "tag": "B-FOOD"},
            {"index": 4, "word": "조각", "tag": "B-UNIT"},
        ]
    }
    ``` 

##### 2. 응답
- 단위당 g으로 변환된 값과 영양정보를 응답으로 보여준다. (영양정보는 100g을 기준으로 보여준다.)
    ```json
    {
        "data": [
            {"index": 1, "word": "김치찌개", "tag": "B-FOOD"},
            {"index": 2, "word": "그릇", "tag": "B-UNIT"},
            {"index": 3, "word": "200", "tag": "gram"},
            ... (영양정보)
            {"index": 4, "word": "치킨", "tag": "B-FOOD"},
            {"index": 5, "word": "조각", "tag": "B-UNIT"},
            {"index": 6, "word": "150", "tag": "gram"},
            ... (영양정보)
        ]
    }
    ``` 