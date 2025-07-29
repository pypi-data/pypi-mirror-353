#!/usr/bin/env python3
"""
Автотест для функций Yandex SpeechKit STT v3 API.
Проверяет работу синхронных и асинхронных функций для распознавания речи.
"""
import os
import sys
import json
import time
import asyncio
from dotenv import load_dotenv

try:
    from yandex_gpt_api import stt_recognize_file, stt_recognize_file_async, stt_get_recognition, stt_get_recognition_async
except ImportError:
    # Добавляем родительскую директорию в путь импорта
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.yandex_gpt_api import stt_recognize_file, stt_recognize_file_async, stt_get_recognition, stt_get_recognition_async

# Загружаем переменные окружения из .env файла
load_dotenv()

# Путь к тестовому аудиофайлу
TEST_FILE_PATH = os.path.join(os.path.dirname(__file__), "Стандартная запись 18.mp3")

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
    print('Пожалуйста, сохраните либо IAM токен, либо API ключ в переменную окружения `IAM_TOKEN` или `API_KEY`.')
    sys.exit(1)

# Проверка наличия FOLDER_ID
if not os.getenv('FOLDER_ID'):
    print('Пожалуйста, установите переменную окружения FOLDER_ID с идентификатором вашей папки Yandex Cloud.')
    sys.exit(1)


def test_sync_recognize_file():
    """
    Тест синхронной отправки файла на распознавание.
    """
    print("\nТестирование синхронной отправки файла на распознавание...")
    
    # Параметры аудиоформата (MP3)
    audio_format = {
        "containerAudio": {
            "containerAudioType": "MP3"
        }
    }
    
    # Настройки распознавания
    language_restriction = {
        "restrictionType": "WHITELIST",
        "languageCode": ["ru-RU"]
    }
    
    try:
        # Отправляем файл на распознавание
        print(f"Отправка файла: {TEST_FILE_PATH}")
        response = stt_recognize_file(
            auth_headers=headers,
            content=TEST_FILE_PATH,
            audio_format=audio_format,
            language_restriction=language_restriction
        )
        
        # Проверяем, что получен id операции
        if response and 'id' in response:
            operation_id = response['id']
            print(f"Получен id операции: {operation_id}")
            
            # Пауза для начала обработки файла на сервере
            print("Ожидание обработки файла (30 секунд)...")
            time.sleep(30)
            
            # Получаем результат распознавания
            recognition_result = stt_get_recognition(headers, operation_id)
            print(f"Получен результат распознавания: {json.dumps(recognition_result, indent=2)}")
            
            # Проверяем наличие результатов в ответе
            if recognition_result:
                print("Тест синхронной отправки файла пройден успешно.")
                return True, operation_id
        
        print("Ошибка: не получен id операции или результаты распознавания.")
        return False, None
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return False, None


async def test_async_recognize_file():
    """
    Тест асинхронной отправки файла на распознавание.
    """
    print("\nТестирование асинхронной отправки файла на распознавание...")
    
    # Параметры аудиоформата (MP3)
    audio_format = {
        "containerAudio": {
            "containerAudioType": "MP3"
        }
    }
    
    # Настройки распознавания
    language_restriction = {
        "restrictionType": "WHITELIST",
        "languageCode": ["ru-RU"]
    }
    
    try:
        # Отправляем файл на распознавание асинхронно
        print(f"Асинхронная отправка файла: {TEST_FILE_PATH}")
        response = await stt_recognize_file_async(
            auth_headers=headers,
            content=TEST_FILE_PATH,
            audio_format=audio_format,
            language_restriction=language_restriction
        )
        
        # Проверяем, что получен id операции
        if response and 'id' in response:
            operation_id = response['id']
            print(f"Получен id операции: {operation_id}")
            
            # Пауза для начала обработки файла на сервере
            print("Ожидание обработки файла (30 секунд)...")
            await asyncio.sleep(30)
            
            # Получаем результат распознавания асинхронно
            recognition_result = await stt_get_recognition_async(headers, operation_id)
            print(f"Получен результат распознавания: {json.dumps(recognition_result, indent=2)}")
            
            # Проверяем наличие результатов в ответе
            if recognition_result:
                print("Тест асинхронной отправки файла пройден успешно.")
                return True
        
        print("Ошибка: не получен id операции или результаты распознавания.")
        return False
            
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return False


def print_recognized_text(recognition_result):
    """
    Вспомогательная функция для извлечения распознанного текста из результата.
    """
    try:
        # Попытка извлечь текст из разных возможных структур ответа
        if 'final' in recognition_result:
            alts = recognition_result['final'].get('alternatives', [])
            if alts:
                return alts[0].get('text', '')
        
        if 'partial' in recognition_result:
            alts = recognition_result['partial'].get('alternatives', [])
            if alts:
                return alts[0].get('text', '')
                
        if 'results' in recognition_result:
            for result in recognition_result['results']:
                if 'alternatives' in result and result['alternatives']:
                    return result['alternatives'][0].get('text', '')
        
        return "Текст не найден в ответе"
    except Exception as e:
        return f"Ошибка при извлечении текста: {e}"


async def test_full_recognition_cycle():
    """
    Тестирование полного цикла распознавания - от отправки файла до получения текста.
    """
    print("\nТестирование полного цикла распознавания...")
    
    success, operation_id = test_sync_recognize_file()
    if not success or not operation_id:
        return False
    
    try:
        # Ждем дополнительное время для завершения обработки
        print("Дополнительное ожидание завершения обработки (10 секунд)...")
        time.sleep(10)
        
        # Получаем результат распознавания
        recognition_result = stt_get_recognition(headers, operation_id)
        
        # Выделяем текст из результата с учетом возможных различных структур ответа
        try:
            # Пробуем разные пути извлечения текста из результата
            if 'result' in recognition_result and 'final' in recognition_result['result'] and 'alternatives' in recognition_result['result']['final']:
                text = recognition_result['result']['final']['alternatives'][0]['text']
            elif 'result' in recognition_result and 'alternatives' in recognition_result['result']:
                text = recognition_result['result']['alternatives'][0]['text']
            else:
                # Выводим структуру ответа для отладки
                print("Структура ответа:")
                print(f"Ключи верхнего уровня: {list(recognition_result.keys())}")
                if 'result' in recognition_result:
                    print(f"Ключи в 'result': {list(recognition_result['result'].keys())}")
                raise KeyError("Не удалось найти текст в структуре ответа")
                
            print(f"Распознанный текст: {text}")
            if text and len(text) > 0:
                print("Тест полного цикла распознавания пройден успешно.")
                return True
            else:
                print("Ошибка: распознанный текст пуст.")
                return False
        except (KeyError, IndexError) as e:
            print(f"Распознанный текст: Текст не найден в ответе")
            print(f"Ошибка: не удалось извлечь распознанный текст: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Ошибка при выполнении полного цикла: {e}")
        return False


async def run_tests():
    """
    Запуск всех тестов.
    """
    print("Запуск тестов Yandex STT API...")
    
    # Запускаем тесты
    # Тест синхронной отправки файла пропускаем, так как он выполняется в test_full_recognition_cycle
    async_result = await test_async_recognize_file()
    full_cycle_result = await test_full_recognition_cycle()
    
    # Выводим общий результат
    print("\nРезультаты тестирования:")
    print(f"Асинхронная отправка файла: {'✓' if async_result else '✗'}")
    print(f"Полный цикл распознавания: {'✓' if full_cycle_result else '✗'}")
    
    # Определяем общий результат
    all_passed = async_result and full_cycle_result
    
    print(f"\nОбщий результат: {'Все тесты пройдены успешно!' if all_passed else 'Некоторые тесты не пройдены.'}")
    return all_passed


if __name__ == "__main__":
    # Запускаем все тесты
    success = asyncio.run(run_tests())
    
    # Устанавливаем код возврата для CI/CD
    sys.exit(0 if success else 1)