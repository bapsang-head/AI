def ner_model(text):
    # NER 모델을 사용하여 텍스트에서 개체명 인식 수행
    # 예시 데이터 반환 (실제 NER 모델 사용)
    # 추후 NER 삽입 예정
    return [
        {"index": 1, "word": "삽겹살", "tag": "B-FOOD"},
        {"index": 2, "word": "2", "tag": "B-QTY"},
        {"index": 3, "word": "인분", "tag": "B-UNIT"},
        {"index": 4, "word": "소주", "tag": "B-FOOD"},
        {"index": 5, "word": "밥", "tag": "B-FOOD"},
        {"index": 6, "word": "3", "tag": "B-QTY"},
        {"index": 7, "word": "공기", "tag": "B-UNIT"}
    ]
