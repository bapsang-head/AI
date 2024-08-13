# KoBERT-NER-Diet

KoBERT를 이용한 Diet Domain 한국어 Named Entity Recognition(NER) 작업을 위한 가이드입니다. 🤗 `Huggingface Transformers` 라이브러리를 활용하여 KoBERT를 손쉽게 사용할 수 있습니다.

## How to use KoBERT on Huggingface Transformers Library

- 기존의 KoBERT를 transformers 라이브러리에서 곧바로 사용할 수 있도록 최적화하였습니다.
  - transformers v2.2.2부터는 개인이 만든 모델을 transformers를 통해 직접 업로드하고 다운로드하여 사용할 수 있습니다.
- Tokenizer를 사용하려면 `utils.py`에서 `KoBERTTokenizer`를 임포트해야 합니다.

```python
from transformers import BertModel
from kobert_tokenizer import KoBERTTokenizer

def load_tokenizer(args):
    bert_tokenizer = KoBERTTokenizer.from_pretrained(pretrained_model_name_or_path="skt/kobert-base-v1")
    return bert_tokenizer
```

## Usage

```bash
$ python3 main.py --model_type kobert --do_train --do_eval
```

- `--write_pred` 옵션을 주면 **evaluation의 prediction 결과**가 `preds` 폴더에 저장됩니다.

## Prediction

```bash
$ python3 predict.py --input_file {INPUT_FILE_PATH} --output_file {OUTPUT_FILE_PATH} --model_dir {SAVED_CKPT_PATH}
```

## Results

| 모델                        | Slot F1 (%) |
|---------------------------|-------------|
| KoBERT                    | 99.00       |
| DistilKoBERT              | 90.00       |
| Bert-Multilingual         | 99.00       |

## 데이터 설명
- **FOOD-B**: 음식 시작 태그
- **FOOD-I**: 음식 안에 있는 태그
- **QTY-B**: 수량 시작 태그
- **QTY-I**: 수량 안에 있는 태그
- **UNIT-B**: 단위 시작 태그

### NER 입력 예시
```
나는 한잔은 아이스 아메리카노를 마시고 디저트는 마카롱 3개를 먹음.
```

### NER 출력 예시
```
나는 [한:QTY-B] [잔:UNIT-B] 은 [아이스:FOOD-B] [아메리카노:FOOD-I] 마시고 디저트는 [마카롱:FOOD-B] [3:QTY-B] [개:UNIT-B] 를 먹음.
```

## References

- [Naver NLP Challenge](https://github.com/naver/nlp-challenge)
- [Huggingface Transformers](https://github.com/huggingface/transformers)
