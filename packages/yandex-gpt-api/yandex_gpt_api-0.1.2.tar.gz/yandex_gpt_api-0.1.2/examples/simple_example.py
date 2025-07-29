#!/usr/bin/env python3
"""
Простой пример использования библиотеки Yandex GPT API.
"""
import os
from dotenv import load_dotenv
from yandex_gpt_api import gpt, gpt_streaming

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка аутентификации
if os.getenv('IAM_TOKEN') is not None:
    iam_token = os.environ['IAM_TOKEN']
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }
elif os.getenv('API_KEY') is not None:
    api_key = os.environ['API_KEY']
    headers = {
        'Authorization': f'Api-Key {api_key}',
    }
else:
    print('Пожалуйста, сохраните либо IAM токен, либо API ключ в соответствующую переменную окружения `IAM_TOKEN` или `API_KEY`.')
    exit()

# Проверка наличия FOLDER_ID
if not os.getenv('FOLDER_ID'):
    print('Пожалуйста, установите переменную окружения FOLDER_ID с идентификатором вашей папки Yandex Cloud.')
    exit()

# Пример использования непотокового режима
print("Пример непотокового режима:")
messages = [
    {
        "role": "system",
        "text": "Вы - полезный ассистент"
    },
    {
        "role": "user",
        "text": "Расскажи короткую историю о роботе"
    }
]
response = gpt(headers, messages)
print(response)

# Пример использования потокового режима
print("\nПример потокового режима:")
for chunk in gpt_streaming(headers, messages):
    print(chunk, end='', flush=True)
print("\n")
