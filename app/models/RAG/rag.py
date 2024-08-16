import requests
from bs4 import BeautifulSoup
from app.services.gpt_service import generate_response  # GPT 모델을 사용하기 위한 함수 임포트

class RAG:
    def extract_nutrition_info(self, html_content):
        # HTML에서 영양 정보를 추출하는 함수
        soup = BeautifulSoup(html_content, 'lxml')
        nutrition_data = []

        # HTML 테이블을 파싱하여 영양 정보를 추출
        for row in soup.select('table.generic.searchResult tr'):
            if len(nutrition_data) >= 10:  # 최대 10개 항목만 추출
                break
            food_link = row.find('a', class_='prominent')
            if food_link:
                food_name = food_link.text.strip()
                # 영양 정보 추출
                nutrition_info = row.find('div', class_='smallText greyText greyLink').text.strip()
                # 영양 정보에서 필요한 부분만 추출
                nutrition_details = nutrition_info.split('|')
                nutrition_details = [detail.strip() for detail in nutrition_details]
                nutrition_data.append((food_name, nutrition_details))

        return nutrition_data

    def search_nutrition_info(self, food_name):
        # FatSecret 웹사이트에서 음식 이름으로 영양 정보를 검색하는 함수
        url = f"https://www.fatsecret.kr/칼로리-영양소/search"
        params = {'q': food_name}
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            # HTML에서 영양 정보 추출
            nutrition_data = self.extract_nutrition_info(response.text) 
            # 영양 정보를 문자열로 변환
            nutrition_info = [f"{name}: {', '.join(details)}" for name, details in nutrition_data]
            # print(nutrition_info)
            return nutrition_info
        else:
            self.logger.error(f"FatSecret search error: {response.text}")  
            return []

    def generate_response_with_rag(self, prompt, food_names, gpt_api_key):
        # GPT 모델을 사용하여 RAG 방식으로 응답 생성
        try:
            # 1단계: 각 음식 이름에 대해 영양 정보 검색
            all_nutrition_info = []
            for food_name in food_names:
                nutrition_info = self.search_nutrition_info(food_name)
                if nutrition_info:
                    all_nutrition_info.extend(nutrition_info)

            # 2단계: 검색된 영양 정보를 프롬프트에 포함
            augmented_prompt = prompt + "\n\n" + "\n".join(all_nutrition_info)

            # 3단계: GPT 모델을 사용하여 응답 생성
            response = generate_response(augmented_prompt, gpt_api_key)
            return response

        except Exception as e:
            self.logger.error(f"Error in generating response with RAG: {e}")  
            return str(e)