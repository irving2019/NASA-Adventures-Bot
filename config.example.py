"""
Пример конфигурационного файла.
Переименуйте этот файл в config.py и заполните реальными значениями.
"""
import os
from typing import Final

# Настройки логирования
LOG_LEVEL: Final = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: Final = os.getenv(
    "LOG_FORMAT",
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
LOG_FILE: Final = os.getenv("LOG_FILE", "bot.log")

# Настройки Redis
REDIS_URL: Final = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_PASSWORD: Final = os.getenv("REDIS_PASSWORD", None)
CACHE_TTL: Final = int(os.getenv("CACHE_TTL", 3600))  # Время жизни кэша в секундах

# Настройки мониторинга
ENABLE_METRICS: Final = os.getenv("ENABLE_METRICS", "true").lower() == "true"
METRICS_PORT: Final = int(os.getenv("METRICS_PORT", 8000))

# Токен для Telegram бота (получить у @BotFather)
BOT_TOKEN: Final = os.getenv(
    "BOT_TOKEN",
    "YOUR_TELEGRAM_BOT_TOKEN"  # Замените на ваш токен
)

# API ключ NASA (получить на https://api.nasa.gov)
NASA_API_KEY: Final = os.getenv(
    "NASA_API_KEY",
    "YOUR_NASA_API_KEY"  # Замените на ваш ключ API
)

# URLs для API NASA
NEO_URL: Final = "https://api.nasa.gov/neo/rest/v1/feed"  # API для астероидов
MARS_PHOTOS_URL: Final = "https://api.nasa.gov/mars-photos/api/v1/rovers/{}/photos"  # API для фото с марсоходов
EARTH_URL: Final = "https://api.nasa.gov/planetary/earth/imagery"  # API для снимков Земли

# Google Custom Search API
GOOGLE_CSE_API_URL: Final = "https://www.googleapis.com/customsearch/v1"
GOOGLE_API_KEY: Final = os.getenv("GOOGLE_API_KEY", "YOUR_GOOGLE_API_KEY")  # Замените на ваш ключ API Google
GOOGLE_CSE_ID: Final = os.getenv("GOOGLE_CSE_ID", "YOUR_GOOGLE_CSE_ID")  # Замените на ваш CSE ID

# Поисковые запросы для изображений
GOOGLE_SEARCH_TYPES: Final = {
    'apod': [
        "hubble deep field galaxy HD",
        "nebula space telescope photograph",
        "spiral galaxy high resolution",
        "ESO VLT telescope image",
        "space observatory photograph HD",
        "cosmic structure NASA ESA",
        "deep space nebula HD",
        "star cluster Hubble photo",
        "planetary nebula high resolution",
        "astronomy observatory image"
    ]
}
