from flask import Flask
from app.api.endpoints.first_GPT_API import first_GPT_API_blueprint
from app.api.endpoints.second_GPT_API import second_GPT_API_blueprint

app = Flask(__name__)

# 블루프린트 등록
app.register_blueprint(first_GPT_API_blueprint, url_prefix='/first_GPT_API')
app.register_blueprint(second_GPT_API_blueprint, url_prefix='/second_GPT_API')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
