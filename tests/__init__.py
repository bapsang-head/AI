import os
import argparse

# ArgumentParser 설정
parser = argparse.ArgumentParser()
parser.add_argument("--input_file", default="sample_pred_in.txt", type=str, help="Input file for prediction")
parser.add_argument("--output_file", default="sample_pred_out.txt", type=str, help="Output file for prediction")
parser.add_argument("--model_dir", default="./app/models/KoBERT_NER/model", type=str, help="Path to save, load model")  # 슬래시 수정
parser.add_argument("--batch_size", default=32, type=int, help="Batch size for prediction")
parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")

# 인자 파싱
pred_config = parser.parse_args([])  # 빈 리스트를 전달하여 기본값 사용

# 현재 작업 디렉토리 출력
print("Current working directory:", os.getcwd())

# 모델 파일 경로 확인
model_file = os.path.join(pred_config.model_dir, 'training_args.bin')
if not os.path.exists(model_file):
    raise FileNotFoundError(f"Cannot find the file: {model_file}")
print("File found:", model_file)
