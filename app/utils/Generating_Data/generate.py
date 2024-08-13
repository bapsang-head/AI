import os
from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import re
from sample import real_entities
import random
class Generate_Data:
    def __init__(self):
        # 환경 변수에서 API 키를 로드
        load_dotenv()
        # 발급받은 API 키 설정
        self.OPENAI_API_KEY = os.getenv("GPT_API_KEY")
        # openai API 키 인증
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)
        self.food_names = real_entities[0]['entity_names']

    # GPT 모델을 사용하여 텍스트를 생성하는 함수 top_p_range=(0.8, 1.0)
    def generate(self, prompts, model='gpt-4o', n=1, temperature_range=(0.6, 1.0), max_tokens=150, top_p_range=1.0):
        """
        GPT 모델을 사용하여 텍스트를 생성하는 함수

        :param prompts: 생성할 텍스트에 대한 프롬프트
        :param model: 사용할 GPT 모델 (기본값 'gpt-4o')
        :param n: 생성할 텍스트 수 (기본값 1)
        :param temperature_range: 출력의 다양성을 제어하는 파라미터 범위 (기본값 (0.5, 0.9))
        :param max_tokens: 생성할 텍스트의 최대 토큰 수 (기본값 150)
        :param top_p_range: 출력의 품질을 제어하는 파라미터 범위 (기본값 (0.8, 1.0))
        :return: 생성된 텍스트 리스트
        """
        
        temperature = random.uniform(*temperature_range)
        top_p = top_p_range
        #top_p = random.uniform(*top_p_range)

        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": prompts}
            ],
            n=n,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p
        )

        texts = [choice.message.content for choice in response.choices]
        return texts


#데이터 입력 생각하기.. 띄어쓰기..? -> 형태소 분석기 이용, FOOD-I 케이스 추가
#랜덤샘플링 필요, 문장 형식 더 댜앙하게, 데이터 형식 바꾸기
    def construct_sentence_prompt(self, style='statement',previous_results=None):
        sampled_food_names = random.sample(self.food_names, 20)
        prompt = (
            f'Generate a {style} BIO tagged Korean sentence data for NER Model training.\n'
            f'Return only data in the same format as the example provided below.\n'
            f'Please ensure that each token, its index, and its BIO tag are separated by a tab character.\n'
            f'Make sure to clearly distinguish between FOOD entities and QTY entities.\n'
            f'Each generated sentence should be clearly separated by a newline character.\n'
            f'Please ensure that all entities are tagged accurately and consistently to maintain high-quality data for NER model training.\n'
            f'Vary the structure of sentences and use diverse phrasings to enhance the dataset.\n'
            f'Avoid generating incomplete sentences; ensure each sentence has a clear subject, verb, and object.\n'
            f'Avoid generating Food of sentences that are similar to the following previously generated Food of sentences:\n'
            #f'Here, previous_results: {previous_results}\n'
            f'referring to the following some entities:{sampled_food_names}\n'
            f'For examples, a complete sentence should look like this:\n'
            #f'Examples:\n'
            f'0\t나는\tO\n'
            f'1\t점심\tO\n'
            f'2\t에\tO\n'
            f'3\t불고기\tFOOD-B\n'
            f'4\t피자\tFOOD-I\n'
            f'5\t를\tO\n'
            f'6\t200\tQTY-B\n'
            f'7\tg\tUNIT-B\n'
            f'8\t과\tO\n'
            f'9\t하이뮨\tFOOD-B\n'
            f'10\t프로틴\tFOOD-I\n'
            f'11\다크초코맛\tFOOD-I\n'
            f'12\t한\tQTY-B\n'
            f'13\t잔\tUNIT-B\n'
            f'14\t을\tO\n'
            f'15\t마셨어\tO\n\n'
            f'0\t나는\tO\n'
            f'1\t오늘\tO\n'
            f'2\t불닭맛\tFOOD-B\n'
            f'3\t닭가슴살\tFOOD-I\n'
            f'4\t을\tO\n'
            f'5\t1\tQTY-B\n'
            f'6\t개\tUNIT-B\n'
            f'7\t와\tO\n'
            f'8\t신라면\tFOOD-B\n'
            f'9\t3\tQTY-B\n'
            f'10\t봉지\tUNIT-B\n'
            f'11\t,\tO\n'
            f'12\t에그\tFOOD-B\n'
            f'13\t샐러드\tFOOD-I\n'
            f'14\t한\tQTY-B\n'
            f'15\t접시\tUNIT-B\n'
            f'16\t를\tO\n'
            f'17\t먹었어\tO\n\n'
            f'0\t오늘\tO\n'
            f'1\t저녁\tO\n'
            f'2\t제육볶음\tFOOD-B\n'
            f'3\t100\tQTY-B\n'
            f'4\tg\tUNIT-B\n'
            f'5\t과\tO\n'
            f'6\t밥\tFOOD-B\n'
            f'7\t한\tQTY-B\n'
            f'8\t공기\tUNIT-B\n'
            f'9\t를\tO\n'
            f'10\t먹었어\tO\n\n'
            f'0\t나\tO\n'
            f'1\t굽네치킨\tFOOD-B\n'
            f'1\t고추바사삭\tFOOD-I\n'
            f'2\t1\tQTY-B\n'
            f'3\t마리\tUNIT-B\n'
            f'4\t먹음\tO\n\n'
            f'0\t스타벅스\tFOOD-B\n'
            f'1\t아이스\tFOOD-I\n'
            f'2\t카라멜\tFOOD-I\n'
            f'3\t라떼\tFOOD-I\n'
            f'4\t열\tQTY-B\n'
            f'5\t잔\tUNIT-B\n'
            f'6\t.\tO\n\n'
            f'0\t맥도날드\tFOOD-B\n'
            f'1\t맥스파이시\tFOOD-I\n'
            f'2\t상하이\tFOOD-I\n'
            f'3\t버거\tFOOD-I\n'
            f'3\t한\tQTY-B\n'
            f'4\t개\tUNIT-B\n'
            f'5\t,\tO\n'
            f'6\t네네치킨\tFOOD-B\n'
            f'7\t스노윙\tFOOD-I\n'
            f'8\t치킨\tFOOD-I\n'
            f'9\t을\tO\n'
            f'10\t두\tQTY-B\n'
            f'11\t마리\tUNIT-B\n'
            f'12\t를\tO\n\n'
            f'13\t먹었어\tO\n\n'
            f'Please avoid generating incomplete tagging and sentences\n'
            f'Data:'
        )
        return prompt


    #미사용 호출 비용 증가 우려
    '''
    # 엔티티 이름을 생성하기 위한 프롬프트를 구성하는 함수
    def construct_entity_prompt(self, class_name, entity_names, k=10):
        prompt = f'These are <{class_name}> entity names. Generate {k} new <{class_name}> entity names including a mix of common dishes, exotic foods, and even some well-known brand names. (just print only entities)\n\n'
        prompt += 'Entity names:\n'
        for e in entity_names:
            if e:  # 빈 문자열이 아닌 경우에만 추가
                prompt += f'- {e}\n'
        prompt += '\nGenerated names:\n-'
        return prompt


    # 생성된 엔티티 이름을 후처리하는 함수
    def postprocess_entities(self, synthetic_entities):
        processed = []
        for ents in synthetic_entities:
            ents = f'- {ents}'.split('\n')
            ents = [e.split('- ')[1].strip() for e in ents if e.startswith('- ')]
            processed += ents
        return processed
    '''

    '''
    #미사용(english data만 생성하는 경우에 사용)
    def construct_labels(generated, entities, class2idx):
        labels = [class2idx['outside']] * len(generated)
        for ent in entities:
            l = class2idx[ent['class_name']]
            for span in re.finditer(ent['entity_name'].lower(), generated.lower()):
                s, e = span.start(), span.end()
                labels[s] = l
                labels[s+1:e] = [l+1] * (e-s-1)
        return labels
    

     #미사용(english data만 생성하는 경우에 사용)
    def sample_entities(self, all_entities):
            # all_entities는 리스트 형태로 전달된다고 가정
            if not all_entities:
                raise ValueError("all_entities is empty or not provided")

            # 적절한 min_k와 max_k 값을 설정
            min_k = 1  # 최소값 (예시)
            max_k = 5  # 최대값 (예시)

            # min_k와 max_k가 정수인지 확인
            if not isinstance(min_k, int) or not isinstance(max_k, int):
                raise TypeError("min_k and max_k must be integers")

            k = np.random.randint(min_k, max_k + 1)

            sampled_entities = []
            for i in range(k):
                entity_class = np.random.choice(all_entities)
                entity_name = np.random.choice(entity_class['entity_names'])
                sampled_entities.append(entity_name)
            
            return sampled_entities
    '''