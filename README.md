# AI

노션에 올린 API 명세서 기준으로 구성한 구조이다

## 환경 변수 설정
이 프로젝트는 환경 변수를 사용합니다.  
`.env` 파일을 프로젝트 루트 디렉토리에 생성하고 gpt 키값을 추가해야 정상적으로 동작합니다.

### 현재 진행 상황 (2024.07.14 기준)
- Flask 애플리케이션을 설정하고 SQLAlchemy를 사용하여 음식 영양 정보와 단위 변환 정보를 저장하는 데이터베이스를 구축
 - OpenAI GPT-3.5 API를 사용하여 음식의 영양 정보와 단위 변환 값을 가져오는 기능을 구현
 - Flask 엔드포인트를 통해 사용자가 입력한 음식 데이터를 처리하고 결과를 반환


#### 입력과 응답 예시
- 입력에서 사용자 전체 입력 문장을 어떻게 이용할 지 고민 중
- 치킨에서 한 조각이 1500g이라는 오류가 있는데 수정 방안 탐색중

```json
{
    "user_input": "나는 점심에 김치찌개를 두 그릇과 치킨 세조각을 먹었어",
    "data": [
        {"index": 0, "word": "나는", "tag": "O"},
        {"index": 1, "word": "점심에", "tag": "O"},
        {"index": 2, "word": "김치찌개", "tag": "B-FOOD"},
        {"index": 3, "word": "를", "tag": "O"},
        {"index": 4, "word": "두", "tag": "B-QTY"},
        {"index": 5, "word": "그릇", "tag": "B-UNIT"},
        {"index": 6, "word": "과", "tag": "O"},
        {"index": 7, "word": "치킨", "tag": "B-FOOD"},
        {"index": 8, "word": "세", "tag": "B-QTY"},
        {"index": 9, "word": "조각", "tag": "B-UNIT"},
        {"index": 10, "word": "을", "tag": "O"},
        {"index": 11, "word": "먹었어", "tag": "O"}
    ]
}

[
    {
        "entities": {
            "FOOD": "김치찌개",
            "GRAM_QTY": 400.0,
            "QTY": "두",
            "UNIT": "그릇"
        },
        "nutrition_info": {
            "calories": 150,
            "carbohydrates": 20.0,
            "fat": 5.0,
            "protein": 8.0
        },
        "task_id": "task_1"
    },
    {
        "entities": {
            "FOOD": "치킨",
            "GRAM_QTY": 1500.0,
            "QTY": "세",
            "UNIT": "조각"
        },
        "nutrition_info": {
            "calories": 250,
            "carbohydrates": 5.0,
            "fat": 15.0,
            "protein": 20.0
        },
        "task_id": "task_2"
    }
]

