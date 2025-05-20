# 🚀 NASA Space Explorer Bot

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/downloads/)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.3.0-blue.svg)](https://docs.aiogram.dev/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Redis](https://img.shields.io/badge/Redis-5.0.1-red.svg)](https://redis.io/)

*Исследуйте космос с помощью современного Telegram-бота, использующего официальные API NASA* 🌌

</div>

## ✨ Возможности

### 🌠 Исследование космоса
- **☄️ Астероиды**: Отслеживание околоземных объектов в реальном времени
- **🔴 Марс**: Актуальные фотографии с марсоходов Curiosity и Perseverance
- **🌍 Земля**: Спутниковые снимки любой точки планеты
- **🌞 Солнечная система**: Подробная информация о планетах и их характеристиках
- **✨ Экзопланеты**: Каталог известных экзопланет с описаниями
- **❓ Викторина**: Космическая викторина разных уровней сложности

### 🛠 Технические особенности
- **🔄 Кэширование**: Оптимизированное хранение данных с Redis
- **📊 Мониторинг**: Prometheus + Grafana для отслеживания производительности
- **🐳 Docker**: Полная контейнеризация для простого развертывания
- **🔍 Админ-панель**: Статистика использования и управление кэшем

## 🚀 Быстрый старт

### 📋 Предварительные требования
- Python 3.11+
- Redis
- Git

### ⚡ Установка

1. **Клонируйте репозиторий**
```bash
git clone https://github.com/your-username/nasa-space-bot.git
cd nasa-space-bot
```

2. **Настройка окружения**
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```

3. **Установка зависимостей**
```bash
pip install -r requirements.txt
```

4. **Настройка конфигурации**
```bash
cp config.example.py config.py
# Отредактируйте config.py, добавив свои токены
```

5. **Запуск бота**
```bash
python run.py
```

## 🐳 Docker

### Запуск через Docker Compose

```bash
docker-compose up --build
```

Это автоматически:
- 🔄 Поднимет Redis для кэширования
- 📊 Настроит Prometheus для метрик
- 📈 Установит Grafana для визуализации
- 🤖 Запустит самого бота

## ⚙️ Конфигурация

### Основные переменные окружения

| Переменная | Описание | Пример |
|------------|----------|---------|
| `BOT_TOKEN` | Токен Telegram бота | `123456:ABC-DEF...` |
| `NASA_API_KEY` | API ключ NASA | `DEMO_KEY` |
| `REDIS_URL` | URL для подключения к Redis | `redis://localhost:6379/0` |

### 🔐 Получение токенов

1. **Telegram Bot Token**:
   - Создайте бота через [@BotFather](https://t.me/BotFather)
   - Получите и скопируйте токен

2. **NASA API Key**:
   - Зарегистрируйтесь на [api.nasa.gov](https://api.nasa.gov/)
   - Получите ключ API в личном кабинете

## 📊 Мониторинг

### Доступные дашборды:
- 🔍 **Prometheus**: `http://localhost:9090`
  - Метрики производительности
  - Статистика запросов
  - Данные о кэшировании

- 📈 **Grafana**: `http://localhost:3000`
  - Визуализация метрик
  - Мониторинг в реальном времени
  - Настраиваемые дашборды

## 🧪 Тестирование

```bash
# Запуск всех тестов с отчетом о покрытии
pytest -v --cov=.

# Запуск конкретного модуля
pytest tests/test_nasa_handlers.py -v
```

## 📦 Структура проекта

```
nasa-space-bot/
├── data/                 # Данные о планетах и марсоходах
├── utils/               # Утилиты (кэш, мониторинг, HTTP)
├── handlers/            # Обработчики команд бота
├── tests/              # Тесты
└── docker/             # Docker конфигурация
```

## 🤝 Вклад в проект

1. 🔀 Форкните репозиторий
2. 🔨 Создайте ветку для новой функции (`git checkout -b feature/amazing`)
3. 🔃 Создайте Pull Request
