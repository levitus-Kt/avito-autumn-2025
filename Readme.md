# Инструкция по запуску автоматизированных тестов

## Требования:

Python 3.8+

Установить зависимости: `pip install pytest requests jsonschema`

## Запуск:

`pytest test_api.py`

Тесты пройдут успешно, если sellerID уникален. Если конфликт — измените диапазон random

Тесты idempotent (используют fixtures)

Все тесты проверяют status и schema