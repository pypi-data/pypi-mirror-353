#!/usr/bin/env python3
"""
Пример асинхронного использования библиотеки Yandex GPT API.
"""
import os
import json
import asyncio
import time
from dotenv import load_dotenv
from yandex_gpt_api import gpt_async, gpt_streaming_httpx

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


def extract_text_from_response(response):
    """Извлекает текст из JSON-ответа API"""
    try:
        data = json.loads(response)
        if 'result' in data and 'alternatives' in data['result']:
            for alt in data['result']['alternatives']:
                if 'message' in alt and 'text' in alt['message']:
                    return alt['message']['text'].strip()
        if 'error' in data:
            return f"Ошибка: {data['error']}"
        return response
    except json.JSONDecodeError:
        return response


async def run_async_example():
    # Пример использования асинхронного непотокового режима
    print("Пример асинхронного непотокового режима:")
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
    
    try:
        response = await gpt_async(headers, messages, timeout=30.0)
        text = extract_text_from_response(response)
        print(text)
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
    
    # Пауза между примерами
    await asyncio.sleep(1)
    
    # Пример использования асинхронного потокового режима
    print("\nПример асинхронного потокового режима:")
    collected_text = ""
    try:
        print("Начинаем потоковый запрос...")
        chunk_count = 0
        async for chunk in gpt_streaming_httpx(headers, messages, timeout=30.0):
            chunk_count += 1
            if chunk:
                print(chunk, end='', flush=True)
                collected_text += chunk
        print(f"\nПолучено {chunk_count} фрагментов текста.")
        print("\n")
    except Exception as e:
        print(f"\nОшибка при выполнении потокового запроса: {e}")
    
    # Пауза между примерами
    await asyncio.sleep(1)
    
    # Пример параллельного выполнения нескольких запросов
    print("\nПример параллельного выполнения нескольких запросов:")
    
    # Создаем разные запросы
    messages1 = [
        {"role": "system", "text": "Вы - полезный ассистент"},
        {"role": "user", "text": "Назови 3 преимущества Python"}
    ]
    
    messages2 = [
        {"role": "system", "text": "Вы - полезный ассистент"},
        {"role": "user", "text": "Назови 3 преимущества асинхронного программирования"}
    ]
    
    # Запускаем запросы параллельно и замеряем время
    start_time = time.time()
    
    try:
        # Выполняем запросы параллельно с таймаутом
        responses = await asyncio.gather(
            gpt_async(headers, messages1, timeout=30.0),
            gpt_async(headers, messages2, timeout=30.0),
            return_exceptions=True  # Это позволит продолжить выполнение, даже если один из запросов завершится с ошибкой
        )
        
        end_time = time.time()
        
        # Выводим результаты
        for i, response in enumerate(responses, 1):
            print(f"\nОтвет {i}:")
            if isinstance(response, Exception):
                print(f"Ошибка: {response}")
            else:
                text = extract_text_from_response(response)
                print(text[:150] + "..." if len(text) > 150 else text)
        
        print(f"\nВремя выполнения параллельных запросов: {end_time - start_time:.2f} секунд")
    
    except Exception as e:
        print(f"Ошибка при выполнении параллельных запросов: {e}")


if __name__ == "__main__":
    # Запуск асинхронных примеров
    asyncio.run(run_async_example())
