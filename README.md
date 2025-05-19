# NASA Space Bot

Телеграм-бот для изучения космоса с помощью NASA API и других открытых источников.

## Основные функции
- Астероиды: данные о сближениях с Землей
- Марс: актуальные фотографии с марсоходов
- Спутниковые снимки Земли по координатам
- Солнечная система: информация о планетах
- Экзопланеты: каталог известных экзопланет
- Космическая викторина
- Админ-команды: статистика, очистка кэша

## Быстрый старт
1. Клонируйте репозиторий
2. Скопируйте config.example.py в config.py и заполните переменные
3. Установите зависимости:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Запустите бота:
   ```bash
   python run.py
   ```

## Docker
- Для запуска используйте docker-compose:
  ```bash
  docker-compose up --build
  ```
- Переменные берутся из config.py или .env

## Переменные
- BOT_TOKEN — токен Telegram-бота
- NASA_API_KEY — ключ NASA API
- REDIS_URL — адрес Redis

## Мониторинг
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## Тесты
```bash
pytest -v --cov=.
```

## Лицензия
MIT
