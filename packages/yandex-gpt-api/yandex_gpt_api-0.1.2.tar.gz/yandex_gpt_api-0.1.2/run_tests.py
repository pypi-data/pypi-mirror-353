#!/usr/bin/env python3
"""
Скрипт для запуска тестов библиотеки Yandex GPT API.
Запускает тесты по отдельности, чтобы избежать проблем с выполнением.
"""
import os
import sys
import subprocess
import argparse
from termcolor import colored


def run_test(test_path, test_name=None):
    """Запускает отдельный тест и возвращает статус его выполнения."""
    cmd = ["python", "-m", "pytest", test_path, "-v"]
    if test_name:
        cmd.append(f"{test_path}::{test_name}")
    
    print(colored(f"Запуск теста: {' '.join(cmd)}", "blue"))
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=60  # Таймаут 60 секунд на каждый тест
        )
        
        if result.returncode == 0:
            print(colored("✓ Тест успешно пройден!", "green"))
            return True
        else:
            print(colored("✗ Тест не пройден!", "red"))
            print(colored("Вывод:", "yellow"))
            print(result.stdout)
            print(colored("Ошибки:", "yellow"))
            print(result.stderr)
            return False
    
    except subprocess.TimeoutExpired:
        print(colored("⚠ Тест прерван по таймауту (60 сек)", "yellow"))
        return False
    except Exception as e:
        print(colored(f"⚠ Ошибка выполнения теста: {e}", "red"))
        return False


def main():
    """Основная функция для запуска тестов."""
    parser = argparse.ArgumentParser(description='Запуск тестов для Yandex GPT API')
    parser.add_argument('--all', action='store_true', help='Запустить все тесты')
    parser.add_argument('--gpt', action='store_true', help='Запустить тесты GPT API')
    parser.add_argument('--stt', action='store_true', help='Запустить тесты STT API')
    parser.add_argument('--speaker', action='store_true', help='Запустить тесты распознавания говорящих')
    
    args = parser.parse_args()
    
    test_files = []
    if args.all or not (args.gpt or args.stt or args.speaker):
        test_files = [
            'tests/test_yandex_gpt_api.py',
            'tests/test_yandex_stt_api.py',
            'tests/test_yandex_stt_speaker_labeling.py'
        ]
    else:
        if args.gpt:
            test_files.append('tests/test_yandex_gpt_api.py')
        if args.stt:
            test_files.append('tests/test_yandex_stt_api.py')
        if args.speaker:
            test_files.append('tests/test_yandex_stt_speaker_labeling.py')
    
    success_count = 0
    total_count = len(test_files)
    
    print(colored(f"Начинаю выполнение {total_count} тестовых файлов:", "blue"))
    
    for test_file in test_files:
        success = run_test(test_file)
        if success:
            success_count += 1
    
    print(colored(f"\nРезультаты: {success_count}/{total_count} тестов успешно выполнены", "blue"))
    
    if success_count == total_count:
        print(colored("Все тесты пройдены успешно!", "green"))
        return 0
    else:
        print(colored("Некоторые тесты не прошли.", "red"))
        return 1


if __name__ == "__main__":
    sys.exit(main())
