import os
import random
import logging

import torch
import numpy as np
from seqeval.metrics import precision_score, recall_score, f1_score, classification_report

from transformers import (
    BertConfig,
    DistilBertConfig,
    ElectraConfig,
    ElectraTokenizer,
    BertTokenizer,
    BertForTokenClassification,
    DistilBertForTokenClassification,
    ElectraForTokenClassification
)
#from tokenization_kobert import KoBertTokenizer
from kobert_tokenizer import KoBERTTokenizer
MODEL_CLASSES = {
    'kobert': (BertConfig, BertForTokenClassification, KoBERTTokenizer),
    'distilkobert': (DistilBertConfig, DistilBertForTokenClassification, KoBERTTokenizer),
    'bert': (BertConfig, BertForTokenClassification, BertTokenizer),
    'kobert-lm': (BertConfig, BertForTokenClassification, KoBERTTokenizer),
    'koelectra-base': (ElectraConfig, ElectraForTokenClassification, ElectraTokenizer),
    'koelectra-small': (ElectraConfig, ElectraForTokenClassification, ElectraTokenizer),
}

MODEL_PATH_MAP = {
    'kobert': 'tgool/kobert',
    'distilkobert': 'tgool/distilkobert',
    'bert': 'bert-base-multilingual-cased',
    'kobert-lm': 'tgool/kobert-lm',
    'koelectra-base': 'tgool/koelectra-base-discriminator',
    'koelectra-small': 'tgool/koelectra-small-discriminator',
}

# 테스트 데이터 읽어오기
def get_test_texts(args):
    texts = []
    current_text = []

    with open(os.path.join(args.data_dir, args.test_file), 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() == "":
                if current_text:
                    texts.append(current_text)
                    current_text = []
            else:
                splits = line.split('\t')
                if len(splits) >= 2:
                    word = splits[1]
                    current_text.append(word)

    # 마지막 텍스트가 처리되지 않은 경우 추가
    if current_text:
        texts.append(current_text)

    return texts


# 
def get_labels(args):
    return [label.strip() for label in open(os.path.join(args.data_dir, args.label_file), 'r', encoding='utf-8')]


def load_tokenizer(args):
    bert_tokenizer = KoBERTTokenizer.from_pretrained(pretrained_model_name_or_path="skt/kobert-base-v1")
    return bert_tokenizer


def init_logger():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)


def set_seed(args):
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    if not args.no_cuda and torch.cuda.is_available():
        torch.cuda.manual_seed_all(args.seed)


def compute_metrics(labels, preds):
    assert len(preds) == len(labels)
    return f1_pre_rec(labels, preds)


def f1_pre_rec(labels, preds):
    return {
        "precision": precision_score(labels, preds, suffix=True),
        "recall": recall_score(labels, preds, suffix=True),
        "f1": f1_score(labels, preds, suffix=True)
    }


def show_report(labels, preds):
    return classification_report(labels, preds, suffix=True)
