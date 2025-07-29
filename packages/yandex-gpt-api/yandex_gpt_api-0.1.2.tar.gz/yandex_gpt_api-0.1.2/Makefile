.PHONY: install test test-safe build publish clean

# Установить зависимости и пакет в режиме разработки
install:
	uv pip install -e ".[dev]"
	# Установить зависимости для запуска тестов
	uv pip install pytest pytest-asyncio termcolor

# Очистить временные файлы и директории сборки
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	find . -name __pycache__ -exec rm -rf {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '.pytest_cache' -exec rm -rf {} +

# Запустить тесты (стандартный метод)
test:
	PYTHONPATH=. python -m pytest tests/ -v

# Запустить тесты безопасным методом (с таймаутом и разделением)
test-safe:
	chmod +x run_tests.py
	PYTHONPATH=. python run_tests.py

# Запустить только тесты для GPT API
test-gpt:
	chmod +x run_tests.py
	PYTHONPATH=. python run_tests.py --gpt

# Запустить только тесты для STT API
test-stt:
	chmod +x run_tests.py
	PYTHONPATH=. python run_tests.py --stt

# Собрать пакет
build: clean
	python -m build

# Опубликовать пакет в PyPI
publish: build
	python -m twine upload dist/*

# Опубликовать пакет в PyPI Test
test-publish: build
	python -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
