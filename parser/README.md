# Парсер email складов Москвы

Собирает email-адреса с сайтов складских компаний Москвы.  
Результат сохраняется в `results.csv`.

## Установка

1. Установи Python 3.10+ если ещё нет: https://python.org
2. Установи зависимости:

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python warehouse_parser.py
```

## Результат

Файл `results.csv` с колонками:

| domain | url | emails |
|---|---|---|
| example.ru | https://example.ru/contacts | info@example.ru |

## Добавить свои сайты

В файле `warehouse_parser.py` найди список `DIRECT_SITES` и добавь нужные URL:

```python
DIRECT_SITES = [
    "https://твой-сайт.ru/contacts",
    ...
]
```
