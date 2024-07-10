import openai


def generate_response(prompt, max_tokens=150, temperature=0.7):
    try:
        response = openai.ChatCompletion.create(
            # model="gpt-4o",
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,  # 생성할 텍스트의 최대 토큰 수
            temperature=temperature,  # 응답의 창의성 수준
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return str(e)
