# AI

## 현재 진행 상황 (2024.09.12 기준)
- RAG 모델 도입 
- api 작동 키를 header로 받아서 진행하는 형식으로 바꿈 (.env에 키값 추가해야 작동)
- api 최대 호출 횟수 제한을 두었음 
    - 초기화 코드 넣었음
- NER 모델 추가 완료 
    - 테스트 확인 완료
- Second_GPT_API에서 음식은 하나만 받는다.
- Second_GPT_API에서 float 형식으로 변경

## GPT model (app/models/GPT/init.py)
- GPT model은 GPT 4o로 통일

## 첫번째 GPT 호출 (app/api/endpoints/first_GPT_API.py)

### 0. 서버가 전해줘야 하는 내용
- 사용자 입력 문장
- api 작동 키
- api 제한 초기화 키(초기화 할떄만 필요)

### 1. 서버에게 유저 입력 문장 요청 
- 서버에 POST로 입력 문장을 요청한다.
- 이를 NER model에 넘겨준다.
- 입력 문장의 예시:
    ```json 
    {
        "user_input": "나는 점심으로 삼겹살 1인분과 소주 한잔을 먹었어"
    }
    ``` 

### 2. NER model (app/service/ner_service.py)
- NER model이 앞선 입력 받은 문장 토대로 개체명을 인식한다.
- 유저 raw 입력 문장을 ko-bert를 통해 인식한 개체명들을 출력하는 함수는 ner_model(user_input) 함수이다.
- 입력 문장은 위의 1번과 같다.
- 응답 결과의 형식은 다음과 같이 나온다. (문장에 태깅된 형태로 출력된다.)
    ```json
    "나는 점심으로 [삽결살:FOOD-B] [1:QTY-B] [인분:UNIT-B] 과 [소주:FOOD-B] [한:QTY-B] [잔:UNIT-B] 을 먹었어"
    ```

### 3. GPT_API 
- NER 모델이 잡아내지 못한 부분까지 잡아내는 응답을 만들어낸다.
- 결과 형식은 다음과 같다.
    ```json
    {
        "data": [
            {
                "food": "삼겹살",
                "quantity": "1",
                "unit": "인분"
            },
            {
                "food": "소주",
                "quantity": "한",
                "unit": "잔"
            }
        ]
    }
    ```

## 두번째 GPT 호출 (app/api/endpoints/second_GPT_API.py)

### 0. 서버가 전해줘야 하는 내용
- 사용자 음식, 단위 세트
- api 작동 키
- api 제한 초기화 키(초기화 할떄만 필요)

### 1. 입력
- 음식, 단위 정보가 DB에 없는 경우 호출하는 경우이다.
- 무조건 음식명과 단위를 전부 넘겨줘야 한다. (null인 경우는 없다.)
    ```json
    {
        "food": "삽겹살",
        "unit": "덩어리"
    }
    ``` 

### 2. 응답
- 단위당 g으로 변환된 값과 영양정보를 응답으로 보여준다. 
- 영양정보는 100g을 기준으로 보여준다. (칼로리, 탄수화물, 단백질, 지방)
- 한 음식당 7개의 정보를 가지고 온다.
    ```json
    {
        "food": "삽겹살",
        "unit": "덩어리",
        "gram": 100.0,
        "Calories": 331.0,
        "Carbohydrates": 0.59,
        "Protein": 17.24,
        "Fat": 28.21
    }    
    ``` 