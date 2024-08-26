import requests
import logging
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
            return nutrition_info
        else:
            self.logger.error(f"FatSecret search error: {response.text}")  
            return []