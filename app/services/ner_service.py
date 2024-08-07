def ner_model(user_input):
    # 예시 구현: 실제 NER 모델 로직으로 교체
    if not user_input:
        return []
    # 예를 들어 NER 모델이 정상적으로 작동하는 경우:
    return [
        {"word": "김치찌개", "tag": "B-FOOD"},
        {"word": "두", "tag": "B-QTY"},
        {"word": "그릇", "tag": "B-UNIT"},
        {"word": "치킨", "tag": "B-FOOD"},
        {"word": "세", "tag": "B-QTY"},
        {"word": "조각", "tag": "B-UNIT"}
    ]
