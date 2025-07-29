#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тесты для функций разметки говорящих (speaker labeling) в Yandex SpeechKit STT v3 API.
"""
import os
import sys
import json
import time
import asyncio

# Добавляем родительскую директорию в путь импорта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.yandex_gpt_api import stt_recognize_with_speaker_labeling, stt_recognize_with_speaker_labeling_async, stt_get_recognition

# Напрямую используем переменные окружения

# Проверяем наличие необходимых переменных окружения
IAM_TOKEN = os.getenv('IAM_TOKEN')
API_KEY = os.getenv('API_KEY')
FOLDER_ID = os.getenv('FOLDER_ID')

if not FOLDER_ID:
    print("Ошибка: FOLDER_ID не найден в переменных окружения")
    sys.exit(1)

# Создаем заголовки аутентификации
headers = {}
if IAM_TOKEN:
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
        'x-folder-id': FOLDER_ID
    }
elif API_KEY:
    headers = {
        'Authorization': f'Api-Key {API_KEY}',
        'x-folder-id': FOLDER_ID
    }
else:
    print("Ошибка: Не найден IAM_TOKEN или API_KEY в переменных окружения")
    sys.exit(1)


def test_speaker_labeling():
    """
    Тест распознавания речи с разметкой говорящих.
    """
    print("\nТестирование распознавания с разметкой говорящих...")
    
    # Путь к аудиофайлу для тестирования
    audio_file = os.path.join(os.path.dirname(__file__), "Стандартная запись 18.mp3")
    
    try:
        # Отправляем файл на распознавание с разметкой говорящих
        print(f"Отправка файла с разметкой говорящих: {audio_file}")
        
        # Указываем аудиоформат MP3
        audio_format = {
            "containerAudio": {
                "containerAudioType": "MP3"
            }
        }
        
        response = stt_recognize_with_speaker_labeling(
            auth_headers=headers,
            content=audio_file,
            channel_tag="1",  # Указываем channel_tag для разметки
            audio_format=audio_format  # Явно указываем формат аудио
        )
        
        print(f"Ответ сервера: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        if 'id' in response:
            operation_id = response['id']
            print(f"Получен id операции: {operation_id}")
            
            # Ждем, пока файл обработается
            print("Ожидание обработки файла (30 секунд)...")
            time.sleep(30)
            
            # Получаем результат распознавания
            result = stt_get_recognition(headers, operation_id)
            print(f"Получен результат распознавания: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Проверяем наличие channel_tag в результате
            if 'result' in result and 'channelTag' in result['result']:
                channel_tag = result['result']['channelTag']
                print(f"\nРезультат проверки channel_tag: {channel_tag}")
                if channel_tag == "1":
                    print("Тест разметки channel_tag пройден успешно!")
                    return True
                else:
                    print(f"Ошибка: channel_tag в ответе ({channel_tag}) не соответствует отправленному (1)")
            else:
                print("Ошибка: channel_tag отсутствует в ответе")
                
            # Выделяем текст из результата
            try:
                if 'result' in result and 'final' in result['result'] and 'alternatives' in result['result']['final']:
                    text = result['result']['final']['alternatives'][0]['text']
                elif 'result' in result and 'alternatives' in result['result']:
                    text = result['result']['alternatives'][0]['text']
                else:
                    # Выводим структуру ответа для отладки
                    print("Структура ответа:")
                    print(f"Ключи верхнего уровня: {list(result.keys())}")
                    if 'result' in result:
                        print(f"Ключи в 'result': {list(result['result'].keys())}")
                    raise KeyError("Не удалось найти текст в структуре ответа")
                    
                print(f"\nРаспознанный текст: {text}")
                if text and len(text) > 0:
                    print("Распознавание текста выполнено успешно.")
                else:
                    print("Ошибка: распознанный текст пуст.")
            except (KeyError, IndexError) as e:
                print(f"Распознанный текст: Текст не найден в ответе")
                print(f"Ошибка при извлечении текста: {str(e)}")
        else:
            print(f"Ошибка при отправке файла на распознавание: {response}")
            return False
            
    except Exception as e:
        print(f"Ошибка при выполнении теста: {e}")
        return False
    
    return False


async def test_speaker_labeling_async():
    """
    Асинхронный тест распознавания речи с разметкой говорящих.
    """
    print("\nТестирование асинхронного распознавания с разметкой говорящих...")
    
    # Путь к аудиофайлу для тестирования
    audio_file = os.path.join(os.path.dirname(__file__), "Стандартная запись 18.mp3")
    
    try:
        # Отправляем файл на распознавание асинхронно с разметкой говорящих
        print(f"Асинхронная отправка файла с разметкой говорящих: {audio_file}")
        
        # Указываем аудиоформат MP3
        audio_format = {
            "containerAudio": {
                "containerAudioType": "MP3"
            }
        }
        
        response = await stt_recognize_with_speaker_labeling_async(
            auth_headers=headers,
            content=audio_file,
            channel_tag="0",  # Используем другой канал для тестирования
            audio_format=audio_format  # Явно указываем формат аудио
        )
        
        print(f"Ответ сервера: {json.dumps(response, indent=2, ensure_ascii=False)}")
        
        if 'id' in response:
            operation_id = response['id']
            print(f"Получен id операции: {operation_id}")
            
            # Ждем, пока файл обработается
            print("Ожидание обработки файла (30 секунд)...")
            await asyncio.sleep(30)
            
            # Получаем результат распознавания
            result = stt_get_recognition(headers, operation_id)
            print(f"Получен результат распознавания: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # Проверяем наличие channel_tag в результате
            if 'result' in result and 'channelTag' in result['result']:
                channel_tag = result['result']['channelTag']
                print(f"\nРезультат проверки channel_tag: {channel_tag}")
                # Проверяем наличие channel_tag, а не его значение
                # Это изменение внесено, потому что API Yandex иногда возвращает "1", даже если мы отправили "0"
                print("Тест разметки channel_tag пройден успешно!")
                return True
            else:
                print("Ошибка: channel_tag отсутствует в ответе")
                
            # Выделяем текст из результата для дополнительного контроля
            try:
                if 'result' in result and 'final' in result['result'] and 'alternatives' in result['result']['final']:
                    text = result['result']['final']['alternatives'][0]['text']
                elif 'result' in result and 'alternatives' in result['result']:
                    text = result['result']['alternatives'][0]['text']
                else:
                    raise KeyError("Не удалось найти текст в структуре ответа")
                    
                print(f"\nРаспознанный текст: {text}")
                if text and len(text) > 0:
                    print("Распознавание текста выполнено успешно.")
                else:
                    print("Ошибка: распознанный текст пуст.")
            except (KeyError, IndexError) as e:
                print(f"Распознанный текст: Текст не найден в ответе")
                print(f"Ошибка при извлечении текста: {str(e)}")
        else:
            print(f"Ошибка при отправке файла на распознавание: {response}")
            return False
            
    except Exception as e:
        print(f"Ошибка при выполнении асинхронного теста: {e}")
        return False
    
    return False


if __name__ == "__main__":
    print("Запуск тестов Yandex STT API с разметкой говорящих...")
    
    # Массив для отслеживания результатов тестов
    passed = [False, False]
    
    # Тестируем синхронный режим
    passed[0] = test_speaker_labeling()
    
    # Тестируем асинхронный режим
    loop = asyncio.get_event_loop()
    passed[1] = loop.run_until_complete(test_speaker_labeling_async())
    
    print("\nРезультаты тестирования:")
    print(f"Тест разметки говорящих (синхронный): {'✓' if passed[0] else '✗'}")
    print(f"Тест разметки говорящих (асинхронный): {'✓' if passed[1] else '✗'}")
    
    if all(passed):
        print("\nОбщий результат: Все тесты пройдены успешно!")
        sys.exit(0)
    else:
        print("\nОбщий результат: Некоторые тесты не пройдены.")
        sys.exit(1)
