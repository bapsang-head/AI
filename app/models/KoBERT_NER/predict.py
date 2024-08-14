import os
import re
import logging
import argparse
from tqdm import tqdm, trange

#from konlpy.tag import Mecab
import numpy as np
import torch
import json
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from transformers import AutoModelForTokenClassification

from app.models.KoBERT_NER.utils import init_logger, load_tokenizer, get_labels

logger = logging.getLogger(__name__)

def get_device(pred_config):
    return "cuda" if torch.cuda.is_available() and not pred_config.no_cuda else "cpu"


def get_args(pred_config):
    return torch.load(os.path.join(pred_config.model_dir, 'training_args.bin'))

def load_model(pred_config, args, device):
    # Load model from Hugging Face Hub using the model name
    model_name = "tgool/Dietkobert"  # Hugging Face에서 올린 모델 이름
    try:
        model = AutoModelForTokenClassification.from_pretrained(model_name)  # Hugging Face Hub에서 모델 로드
        model.to(device)
        model.eval()
        logger.info("***** Model Loaded from Hugging Face Hub *****")
    except Exception as e:
        raise Exception(f"Failed to load model from Hugging Face Hub: {str(e)}")

    return model

def add_space_around_units(text):
    # 숫자와 단위 사이에 공백을 추가하는 정규 표현식
    text = re.sub(r'([\d]+(?:\.\d+)?)(개|봉지|근|그릇|컵|잔|g|그램|kg|킬로그램|리터|ml|밀리리터|포기|줄|장|병|팩|조각|쪽|스푼|숟가락|젓가락|접시|마리|모금|입|캔|덩어리|알|줄기|단위|숟갈|그램|리터|cc|입술|조각|장|그루|송이|스틱|봉|통|팩트|티스푼|테이블스푼|티스푼|조각|병|인분|주먹|공기|대접|그람|그램|그렘|꼬치|)', r'\1 \2', text)
    
    # 한글 숫자와 단위 사이에 공백을 추가하는 정규 표현식
    text = re.sub(r'(한|두|세|네|다섯|여섯|일곱|여덟|아홉|열|반)(개|봉지|근|그릇|컵|잔|g|그램|kg|킬로그램|리터|ml|밀리리터|포기|줄|장|병|팩|조각|쪽|스푼|숟가락|젓가락|접시|마리|모금|입|캔|덩어리|알|줄기|단위|숟갈|그램|리터|cc|입술|조각|장|그루|송이|스틱|봉|통|팩트|티스푼|테이블스푼|티스푼|조각|병|인분|주먹|공기|대접|그람|그램|그렘|꼬치|)', r'\1 \2', text)
    
    # 한글 숫자와 단위 사이에 공백을 추가하는 정규 표현식(한자인 우리말 케이스)
    text = re.sub(r'(?<!\S)(일|이|삼|사|오|육|칠|팔|구|십)(인분|리터|그램|그람|그렘|g|kg|킬로그램|ml|밀리리터)(?!\S)', r'\1 \2', text)
    
    # 단위와 조사 사이에 공백을 추가하는 정규 표현식
    text = re.sub(r'(개|봉지|근|그릇|컵|잔|g|그램|kg|킬로그램|%|리터|ml|밀리리터|포기|줄|장|병|팩|조각|쪽|스푼|숟가락|젓가락|접시|마리|모금|입|캔|덩어리|알|줄기|단위|숟갈|그램|리터|cc|조각|장|그루|송이|스틱|봉|통|팩트|티스푼|테이블스푼|티스푼|조각|병|인분|주먹|공기|대접|그람|그램|그렘|꼬치|})(을|를|와|과|에|에서|으로|로|은|는|도|만|까지|부터|밖에|의|뿐|마다|대로|데|만큼|씩|식|나|이나|하고|이랑|랑|)', r'\1 \2', text)
    
    return text

def remove_last_josa(word):
    # 두 글자 조사 목록
    two_char_josa = ['이랑', '이나', '까지', '하고', '으로', '부터', '밖에', '에서', '같이', '마다', '대로', '만큼']

    # 한 글자 조사 목록
    one_char_josa = ['을', '를', '와', '에', '뿐', '로', '의', '은', '는', '랑', '만', '데', '과', '도']

    # 단어의 마지막 두 글자가 조사인 경우 제거
    if len(word) > 1 and word[-2:] in two_char_josa:
        return word[:-2]  # 두 글자 조사가 있다면 제거

    # '도'가 연속으로 있을 경우 마지막 '도'만 제거
    if word.endswith("도도"):
        return word[:-1]  # 마지막 '도'만 제거
    
    # '과' 앞에 '사'가 있을 경우 제거하지 않도록 처리
    if len(word) ==2 and word[1] == '과' and word[0] == '사':
        return word  # '사'가 앞에 있으므로 원래 단어 반환
    
    # 단어의 마지막 한 글자가 조사인 경우 제거
    if word and word[-1] in one_char_josa:
        return word[:-1]  # 한 글자 조사가 있다면 제거

    return word  # 조사 아니면 원래 단어 반환

# output 음식 옆 조사 제거 필요
def read_input_file(pred_config):
    #mecab = Mecab()
    lines = []
    
    with open(pred_config.input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            line = add_space_around_units(line)
            words = line.split()
            #words = mecab.morphs(line)  # 형태소 단위로 분리
            lines.append(words)

    return lines

def process_input_text(input_text):
    # 입력된 텍스트를 처리하는 함수
    line = input_text.strip()  # 텍스트의 앞뒤 공백 제거
    line = add_space_around_units(line)  # 특정 단위 주위에 공백 추가
    words = line.split()  # 공백을 기준으로 단어 분리
    # words = mecab.morphs(line)  # 형태소 단위로 분리 (필요 시 주석 해제)
    return words  # 리스트 반환

def convert_input_file_to_tensor_dataset(lines,
                                         pred_config,
                                         args,
                                         tokenizer,
                                         pad_token_label_id,
                                         cls_token_segment_id=0,
                                         pad_token_segment_id=0,
                                         sequence_a_segment_id=0,
                                         mask_padding_with_zero=True):
    # Setting based on the current model type
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    unk_token = tokenizer.unk_token
    pad_token_id = tokenizer.pad_token_id

    all_input_ids = []
    all_attention_mask = []
    all_token_type_ids = []
    all_slot_label_mask = []

    for words in lines:
        tokens = []
        slot_label_mask = []
        for word in words:
            word_tokens = tokenizer.tokenize(word)
            if not word_tokens:
                word_tokens = [unk_token]  # For handling the bad-encoded word
            tokens.extend(word_tokens)
            # Use the real label id for the first token of the word, and padding ids for the remaining tokens
            slot_label_mask.extend([0] + [pad_token_label_id] * (len(word_tokens) - 1))

        # Account for [CLS] and [SEP]
        special_tokens_count = 2
        if len(tokens) > args.max_seq_len - special_tokens_count:
            tokens = tokens[: (args.max_seq_len - special_tokens_count)]
            slot_label_mask = slot_label_mask[:(args.max_seq_len - special_tokens_count)]

        # Add [SEP] token
        tokens += [sep_token]
        token_type_ids = [sequence_a_segment_id] * len(tokens)
        slot_label_mask += [pad_token_label_id]

        # Add [CLS] token
        tokens = [cls_token] + tokens
        token_type_ids = [cls_token_segment_id] + token_type_ids
        slot_label_mask = [pad_token_label_id] + slot_label_mask

        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # The mask has 1 for real tokens and 0 for padding tokens. Only real tokens are attended to.
        attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)

        # Zero-pad up to the sequence length.
        padding_length = args.max_seq_len - len(input_ids)
        input_ids = input_ids + ([pad_token_id] * padding_length)
        attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
        token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)
        slot_label_mask = slot_label_mask + ([pad_token_label_id] * padding_length)

        all_input_ids.append(input_ids)
        all_attention_mask.append(attention_mask)
        all_token_type_ids.append(token_type_ids)
        all_slot_label_mask.append(slot_label_mask)

    # Change to Tensor
    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long)
    all_attention_mask = torch.tensor(all_attention_mask, dtype=torch.long)
    all_token_type_ids = torch.tensor(all_token_type_ids, dtype=torch.long)
    all_slot_label_mask = torch.tensor(all_slot_label_mask, dtype=torch.long)

    dataset = TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids, all_slot_label_mask)

    return dataset


def convert_input_list_to_tensor_dataset(lines,
                                         pred_config,
                                         args,
                                         tokenizer,
                                         pad_token_label_id,
                                         cls_token_segment_id=0,
                                         pad_token_segment_id=0,
                                         sequence_a_segment_id=0,
                                         mask_padding_with_zero=True):
    # 현재 모델 유형에 따라 설정
    cls_token = tokenizer.cls_token
    sep_token = tokenizer.sep_token
    unk_token = tokenizer.unk_token
    pad_token_id = tokenizer.pad_token_id

    all_input_ids = []
    all_attention_mask = []
    all_token_type_ids = []
    all_slot_label_mask = []

    for words in lines:  # lines는 리스트의 리스트 형태입니다.
        tokens = []
        slot_label_mask = []
        for word in words:
            word_tokens = tokenizer.tokenize(word)
            if not word_tokens:
                word_tokens = [unk_token]  # 잘못 인코딩된 단어 처리
            tokens.extend(word_tokens)
            slot_label_mask.extend([0] + [pad_token_label_id] * (len(word_tokens) - 1))

        # [CLS] 및 [SEP]를 고려
        special_tokens_count = 2
        if len(tokens) > args.max_seq_len - special_tokens_count:
            tokens = tokens[: (args.max_seq_len - special_tokens_count)]
            slot_label_mask = slot_label_mask[:(args.max_seq_len - special_tokens_count)]

        # [SEP] 토큰 추가
        tokens += [sep_token]
        token_type_ids = [sequence_a_segment_id] * len(tokens)
        slot_label_mask += [pad_token_label_id]

        # [CLS] 토큰 추가
        tokens = [cls_token] + tokens
        token_type_ids = [cls_token_segment_id] + token_type_ids
        slot_label_mask = [pad_token_label_id] + slot_label_mask

        input_ids = tokenizer.convert_tokens_to_ids(tokens)

        # 마스크 설정
        attention_mask = [1 if mask_padding_with_zero else 0] * len(input_ids)

        # 시퀀스 길이에 맞게 제로 패딩
        padding_length = args.max_seq_len - len(input_ids)
        input_ids = input_ids + ([pad_token_id] * padding_length)
        attention_mask = attention_mask + ([0 if mask_padding_with_zero else 1] * padding_length)
        token_type_ids = token_type_ids + ([pad_token_segment_id] * padding_length)
        slot_label_mask = slot_label_mask + ([pad_token_label_id] * padding_length)

        all_input_ids.append(input_ids)
        all_attention_mask.append(attention_mask)
        all_token_type_ids.append(token_type_ids)
        all_slot_label_mask.append(slot_label_mask)

    # 텐서로 변환
    all_input_ids = torch.tensor(all_input_ids, dtype=torch.long)
    all_attention_mask = torch.tensor(all_attention_mask, dtype=torch.long)
    all_token_type_ids = torch.tensor(all_token_type_ids, dtype=torch.long)
    all_slot_label_mask = torch.tensor(all_slot_label_mask, dtype=torch.long)

    dataset = TensorDataset(all_input_ids, all_attention_mask, all_token_type_ids, all_slot_label_mask)

    return dataset




def predict(user_input, pred_config):
    # 모델과 인자 로드
    args = get_args(pred_config)  # 모델 학습 시 사용된 인자 불러오기
    device = get_device(pred_config)  # 사용할 디바이스 설정 (CUDA 또는 CPU)
    model = load_model(pred_config, args, device)  # 모델 로드
    label_lst = get_labels(args)  # 라벨 리스트 불러오기
    logger.info(args)
    
    # 사용자 입력을 리스트 형태로 변환
    lines = [process_input_text(user_input)]  # 입력을 리스트로 변환
    print(lines)
    pad_token_label_id = torch.nn.CrossEntropyLoss().ignore_index  # 패딩 토큰의 라벨 ID 설정
    tokenizer = load_tokenizer(args)  # 토크나이저 로드
    
    # 입력을 TensorDataset으로 변환
    dataset = convert_input_list_to_tensor_dataset(lines, pred_config, args, tokenizer, pad_token_label_id)  # TensorDataset으로 변환
    # 예측 수행
    sampler = SequentialSampler(dataset)  # 시퀀스 샘플러 생성
    data_loader = DataLoader(dataset, sampler=sampler, batch_size=pred_config.batch_size)  # DataLoader 생성

    all_slot_label_mask = None  # 모든 슬롯 라벨 마스크 초기화
    preds = None  # 예측값 초기화

    for batch in tqdm(data_loader, desc="Predicting"):  # 데이터 로더를 통해 배치 단위로 예측 수행
        batch = tuple(t.to(device) for t in batch)  # 배치를 디바이스에 올리기
        with torch.no_grad():  # 그라디언트 계산 비활성화
            inputs = {
                "input_ids": batch[0],  # 입력 ID
                "attention_mask": batch[1],  # 어텐션 마스크
                "labels": None  # 라벨은 없음
            }
            if args.model_type != "distilkobert":  # 모델 타입이 distilkobert가 아닐 경우
                inputs["token_type_ids"] = batch[2]  # 토큰 타입 ID 추가
            outputs = model(**inputs)  # 모델 입력 및 출력 얻기
            logits = outputs[0]  # 로짓값

            if preds is None:  # 첫번째 배치인 경우
                preds = logits.detach().cpu().numpy()  # 예측값 저장
                all_slot_label_mask = batch[3].detach().cpu().numpy()  # 슬롯 라벨 마스크 저장
            else:  # 이후 배치인 경우
                preds = np.append(preds, logits.detach().cpu().numpy(), axis=0)  # 예측값 추가
                all_slot_label_mask = np.append(all_slot_label_mask, batch[3].detach().cpu().numpy(), axis=0)  # 슬롯 라벨 마스크 추가

    preds = np.argmax(preds, axis=2)  # 예측값의 최대값 인덱스 찾기
    slot_label_map = {i: label for i, label in enumerate(label_lst)}  # 인덱스를 라벨로 매핑
    preds_list = [[] for _ in range(preds.shape[0])]  # 예측값 리스트 초기화

    for i in range(preds.shape[0]):  # 예측값 리스트 채우기
        for j in range(preds.shape[1]):
            if all_slot_label_mask[i, j] != pad_token_label_id:  # 패딩 토큰이 아닌 경우
                preds_list[i].append(slot_label_map[preds[i][j]])  # 예측값 추가

    # 결과를 출력할 변수 초기화
    output_lines = []

    for words, preds in zip(lines, preds_list):  # 입력 단어와 예측값 묶기
        line = ""
        for idx, (word, pred) in enumerate(zip(words, preds)):  # 단어와 예측 라벨 묶기
            if pred == 'O':  # 예측 라벨이 'O'인 경우
                line += word + " "  # 단어만 추가
            else:  # 예측 라벨이 'O'가 아닌 경우
                if pred == 'FOOD-B':
                    if idx + 1 < len(preds) and preds[idx + 1] == 'FOOD-I':
                        line += "[{}:{}] ".format(word, pred)  # FOOD-B 추가
                    else:
                        word = remove_last_josa(word)
                        line += "[{}:{}] ".format(word, pred)  # 단어와 예측 라벨 추가
                elif pred == 'FOOD-I':
                    word = remove_last_josa(word)
                    line += "[{}:{}] ".format(word, pred)  # 단어와 예측 라벨 추가
                else:
                    line += "[{}:{}] ".format(word, pred)  # 단어와 예측 라벨 추가

        output_lines.append(line.strip())  # 결과 리스트에 추가
    print(output_lines)
    logger.info("Prediction Done!")  # 예측 완료 로그 출력
    return output_lines  # 출력 결과 반환


if __name__ == "__main__":
    init_logger()
    parser = argparse.ArgumentParser()

    parser.add_argument("--input_file", default="sample_pred_in.txt", type=str, help="Input file for prediction")
    parser.add_argument("--output_file", default="sample_pred_out.txt", type=str, help="Output file for prediction")
    parser.add_argument("--model_dir", default="./model", type=str, help="Path to save, load model")

    parser.add_argument("--batch_size", default=32, type=int, help="Batch size for prediction")
    parser.add_argument("--no_cuda", action="store_true", help="Avoid using CUDA when available")

    pred_config = parser.parse_args()
    predict("난 저녁에 우삼겹을 300g과 김치 두조각 닭가슴살 한덩어리, 밥 한그릇을 먹었어. 오뎅도 한접시 먹었네",pred_config)
