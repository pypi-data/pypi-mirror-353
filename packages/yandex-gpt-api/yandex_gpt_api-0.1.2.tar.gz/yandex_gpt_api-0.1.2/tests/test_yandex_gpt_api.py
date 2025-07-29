#!/usr/bin/env python3
"""
Автотест для библиотеки взаимодействия с Yandex GPT API.
Проверяет работу синхронных и асинхронных функций, включая потоковый режим.
"""
import os
import sys
import json
import asyncio
import pytest
from dotenv import load_dotenv

try:
    from yandex_gpt_api import gpt, gpt_async, gpt_streaming, gpt_streaming_httpx
except ImportError:
    # Добавляем родительскую директорию в путь импорта
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.yandex_gpt_api import gpt, gpt_async, gpt_streaming, gpt_streaming_httpx

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка аутентификации для тестов
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
    sys.exit(1)

# Проверка наличия FOLDER_ID
if not os.getenv('FOLDER_ID'):
    print('Пожалуйста, установите переменную окружения FOLDER_ID с идентификатором вашей папки Yandex Cloud.')
    sys.exit(1)


def test_sync_mode():
    """
    Тест синхронного режима работы API.
    """
    print("\nТестирование синхронного режима...")
    
    # Тестовые сообщения
    messages = [
        {
            "role": "system",
            "text": "Вы - полезный ассистент"
        },
        {
            "role": "user",
            "text": "Ответь одним словом: привет"
        }
    ]
    
    # Выполняем запрос
    try:
        response = gpt(headers, messages)
        print(f"Получен ответ: {response}")
        
        # Проверяем, что ответ содержит JSON
        try:
            data = json.loads(response)
            if 'result' in data and 'alternatives' in data['result']:
                for alt in data['result']['alternatives']:
                    if 'message' in alt and 'text' in alt['message']:
                        print(f"Текст ответа: {alt['message']['text']}")
            print("Тест синхронного режима пройден успешно.")
            assert True
        except json.JSONDecodeError:
            print(f"Ошибка при разборе JSON: {response}")
            return False
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return False


@pytest.mark.asyncio
async def test_async_mode():
    """
    Тест асинхронного режима работы API.
    """
    print("\nТестирование асинхронного режима...")
    
    # Тестовые сообщения
    messages = [
        {
            "role": "system",
            "text": "Вы - полезный ассистент"
        },
        {
            "role": "user",
            "text": "Ответь одним словом: привет"
        }
    ]
    
    # Выполняем запрос
    try:
        response = await gpt_async(headers, messages)
        print(f"Получен ответ: {response}")
        
        # Проверяем, что ответ содержит JSON
        try:
            data = json.loads(response)
            if 'result' in data and 'alternatives' in data['result']:
                for alt in data['result']['alternatives']:
                    if 'message' in alt and 'text' in alt['message']:
                        print(f"Текст ответа: {alt['message']['text']}")
            print("Тест асинхронного режима пройден успешно.")
            assert True
        except json.JSONDecodeError:
            print(f"Ошибка при разборе JSON: {response}")
            return False
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return False


def test_streaming_mode():
    """
    Тест синхронного потокового режима работы API.
    """
    print("\nТестирование синхронного потокового режима...")
    
    # Тестовые сообщения
    messages = [
        {
            "role": "system",
            "text": "Вы - полезный ассистент"
        },
        {
            "role": "user",
            "text": "Ответь коротко: привет"
        }
    ]
    
    # Выполняем запрос
    try:
        full_response = ""
        chunks_received = 0
        
        # Получаем ответ по частям
        for chunk in gpt_streaming(headers, messages):
            chunks_received += 1
            full_response += chunk
            print(f"Получен фрагмент {chunks_received}: {chunk}")
        
        print(f"Всего получено фрагментов: {chunks_received}")
        print(f"Полный ответ: {full_response}")
        
        if chunks_received > 0 and full_response:
            print("Тест синхронного потокового режима пройден успешно.")
            assert True
        else:
            print("Ошибка: не получены фрагменты ответа.")
            assert False
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return False


@pytest.mark.asyncio
async def test_streaming_async_mode():
    """
    Тест асинхронного потокового режима работы API.
    """
    print("\nТестирование асинхронного потокового режима...")
    
    # Тестовые сообщения
    messages = [
        {
            "role": "system",
            "text": "Вы - полезный ассистент"
        },
        {
            "role": "user",
            "text": "Ответь коротко: привет"
        }
    ]
    
    # Выполняем запрос
    try:
        full_response = ""
        chunks_received = 0
        
        # Получаем ответ по частям асинхронно
        async for chunk in gpt_streaming_httpx(headers, messages):
            chunks_received += 1
            full_response += chunk
            print(f"Получен фрагмент {chunks_received}: {chunk}")
        
        print(f"Всего получено фрагментов: {chunks_received}")
        print(f"Полный ответ: {full_response}")
        
        if chunks_received > 0 and full_response:
            print("Тест асинхронного потокового режима пройден успешно.")
            return True
        else:
            print("Ошибка: не получены фрагменты ответа.")
            return False
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return False


async def run_tests():
    """
    Запуск всех тестов.
    """
    print("Запуск тестов Yandex GPT API...")
    
    # Запускаем тесты
    sync_result = test_sync_mode()
    async_result = await test_async_mode()
    streaming_result = test_streaming_mode()
    streaming_async_result = await test_streaming_async_mode()
    
    # Выводим общий результат
    print("\nРезультаты тестирования:")
    print(f"Синхронный режим: {'✓' if sync_result else '✗'}")
    print(f"Асинхронный режим: {'✓' if async_result else '✗'}")
    print(f"Синхронный потоковый режим: {'✓' if streaming_result else '✗'}")
    print(f"Асинхронный потоковый режим: {'✓' if streaming_async_result else '✗'}")
    
    # Определяем общий результат
    all_passed = sync_result and async_result and streaming_result and streaming_async_result
    
    print(f"\nОбщий результат: {'Все тесты пройдены успешно!' if all_passed else 'Некоторые тесты не пройдены.'}")
    return all_passed


if __name__ == "__main__":
    # Запускаем все тесты
    success = asyncio.run(run_tests())
    
    # Устанавливаем код возврата для CI/CD
    sys.exit(0 if success else 1)
