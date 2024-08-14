import argparse
from ..models.KoBERT_NER.predict import predict  # predict.py에서 predict 함수 임포트

def ner_model(user_input):
    if not user_input:
        return []
    
    # ArgumentParser 설정
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", default="sample_pred_in.txt", type=str, help="Input file for prediction")
    parser.add_argument("--output_file", default="sample_pred_out.txt", type=str, help="Output file for prediction")
    parser.add_argument("--model_dir", default="./app/models/KoBERT_NER/model", type=str, help="Path to save, load model")
    parser.add_argument("--data_dir", default="./app/models/KoBERT_NER/data", type=str, help="Path to load label")
    parser.add_argument("--batch_size", default=32, type=int, help="Batch size for prediction")
    parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")

    # 인자 파싱
    pred_config = parser.parse_args([])  # 빈 리스트를 전달하여 기본값 사용

    # 예측 수행
    result = predict(user_input, pred_config)  # 예측 수행
    
    return result  # NER 모델의 출력 반환
