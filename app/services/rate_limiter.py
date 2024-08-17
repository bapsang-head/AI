from functools import wraps
from flask import jsonify
from datetime import datetime, timedelta
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_calls):
        """
        RateLimiter 클래스 초기화.
        :param max_calls: 하루에 허용할 최대 API 호출 수.
        """
        self.max_calls = max_calls
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
                self.call_count = 0
                self.last_reset_date = today

            # 호출 횟수가 최대 허용치를 넘으면 에러 반환
            if self.call_count >= self.max_calls:
                return jsonify({"error": "API call limit exceeded for today"}), 429

            # 호출 횟수 증가
            self.call_count += 1

            # 현재 호출 횟수를 로깅
            logger.info(f"Current API call count: {self.call_count} out of {self.max_calls} allowed for {today}.")
            
            # 실제 API 함수 호출
            return f(*args, **kwargs)
        
        return decorated_function
