from flask import Blueprint, request, jsonify
from app.services.gpt_service import process_data 

diet_bp = Blueprint('diet', __name__)

@diet_bp.route('/diet', methods=['POST'])
def handle_diet():
    data = request.json
    result = process_data(data)
    return jsonify(result)
