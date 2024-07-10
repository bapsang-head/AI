# AI

노션에 올린 API 명세서 기준으로 구성한 구조이다

## 환경 변수 설정

이 프로젝트는 환경 변수를 사용합니다.  
`.env` 파일을 프로젝트 루트 디렉토리에 생성하고 gpt 키값을 추가해야 정상적으로 동작합니다.

### 현재 진행 상황

Flask를 통해서 간단한 예제를 GPT 3.5 turbo를 통해 응답을 생성하는 과정을 성공

#### 입력 예시

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
