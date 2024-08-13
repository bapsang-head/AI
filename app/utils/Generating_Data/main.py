import os
from generate import Generate_Data
from tqdm import tqdm
import time
import json


def generate_ner_data(data_make, num_batches, batch_size):
    data = []
    previous_results = []  # 이전 결과를 매 시행마다 초기화

    for _ in tqdm(range(num_batches)):
        # 문장 생성을 위한 프롬프트 생성
        batch_prompts = data_make.construct_sentence_prompt(previous_results)
        # GPT를 통해 문장 생성
        batch_generated = data_make.generate(batch_prompts, n=batch_size)
        # "example"이 포함되지 않은 문장 필터링
        batch_generated = [sentence for sentence in batch_generated if "example" not in sentence]
        print(batch_generated)  # 생성된 문장 출력
        data.append(batch_generated)
        # 이전 결과를 현재 배치 결과로 덮어씀
        previous_results = batch_generated
        # 각 배치 사이에 10초간 휴식
        time.sleep(5)

    # 데이터를 하나의 문자열로 합침
    data = "\n".join([item for sublist in data for item in sublist])

    return data

def save_data(data, filename):
    with open(filename, "w") as file:
        file.write(data)

def main():
    data_make = Generate_Data()  # 데이터 생성 객체 초기화
    total_ner_data = []
    num_batches = 10
    batch_size = 20

    for _ in range(num_batches):
        ner_data = generate_ner_data(data_make, 1, batch_size)
        total_ner_data.append(ner_data)

    total_ner_data = "\n".join(total_ner_data)
    save_data(total_ner_data, "train_final_need_edit1.txt")

if __name__ == "__main__":
    main()
