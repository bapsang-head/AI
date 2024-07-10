from flask import Blueprint, request, jsonify
from app.services.gpt_service import process_data

# Blueprint 생성
diet_bp = Blueprint('diet', __name__)

@diet_bp.route('/api/diet', methods=['POST'])
def diet():
    """
    POST 요청을 처리하여 입력 데이터를 바탕으로 음식 정보를 반환합니다.
    """
    if request.content_type != 'application/json':
        return jsonify({"error": "Content-Type must be application/json"}), 415
    
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        tagged_data = data.get('data')
        
        if not user_input or not tagged_data:
            return jsonify({"error": "user_input and tagged data are required"}), 400

        response_data = process_data(tagged_data)
        return jsonify(response_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
