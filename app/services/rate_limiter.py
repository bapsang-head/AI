from functools import wraps
from flask import jsonify, request
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_calls, call_initialization_key):
        """
        RateLimiter 클래스 초기화.
        :param max_calls: 하루에 허용할 최대 API 호출 수.
        :param call_initialization_key: 호출 초기화를 위한 키 값.
        """
        self.max_calls = max_calls
        self.call_initialization_key = call_initialization_key  # 호출 초기화 키 저장
        self.call_count = 0
        self.last_reset_date = datetime.now().date()

    def limit_api_calls(self, f):
        """
        API 호출을 제한하는 데코레이터.
        호출 횟수가 제한을 초과하면 429 에러를 반환.
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            today = datetime.now().date()
            
            # 날짜가 바뀌었으면 호출 카운터를 초기화
            if today != self.last_reset_date:
                self.reset_calls()

            # 호출 초기화 로직
            init_key = request.headers.get('CALL_INITIALIZATION')
            if init_key and init_key.strip() == self.call_initialization_key.strip():
                self.reset_calls()  # 호출 횟수 초기화
                return jsonify({"message": "API call count has been reset"}), 200

            # 호출 횟수가 최대 허용치를 넘으면 에러 반환
            if self.call_count >= self.max_calls:
                logger.warning(f"API call limit exceeded: {self.call_count} out of {self.max_calls}")
                return jsonify({"error": "API call limit exceeded for today"}), 429

            # 호출 횟수 증가
            self.call_count += 1
            logger.info(f"API call count incremented: {self.call_count} out of {self.max_calls}.")

            # 실제 API 함수 호출
            return f(*args, **kwargs)
        
        return decorated_function
    
    def reset_calls(self):
        """
        호출 횟수를 초기화하는 메서드.
        """
        self.call_count = 0
        self.last_reset_date = datetime.now().date()
        logger.info("API call count has been reset.")
