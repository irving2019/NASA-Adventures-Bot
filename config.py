"""
Конфигурационный файл с настройками бота и API ключами
"""
import os


# Токен для Telegram бота
BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    "8102984967:AAFwnJhnoPL7wWpp-b5yZ8Y7DMJ9LYe2wyA"
)

# API ключ NASA
NASA_API_KEY = os.getenv(
    "NASA_API_KEY",
    "wig5B0Q0rgAEiEbnfV2r6wXBPU7DnLVd81mGFay0"
)

# URLs для API NASA
APOD_URL = "https://apod.nasa.gov/apod/astropix.html"
NEO_URL = "https://api.nasa.gov/neo/rest/v1/feed"
MARS_PHOTOS_URL = "https://api.nasa.gov/mars-photos/api/v1/rovers/{}/photos"  # Убедились, что URL корректен
EARTH_URL = "https://api.nasa.gov/planetary/earth/imagery"

# URLs для API МКС
ISS_LOCATION_URL = "http://api.open-notify.org/iss-now.json"
ISS_CREW_URL = "http://api.open-notify.org/astros.json"
ISS_PASS_URL = "http://api.open-notify.org/iss-pass.json"

# API для запусков и других данных
LAUNCHES_URL = "https://ll.thespacedevs.com/2.2.0/launch/upcoming"
EVENTS_URL = "https://ll.thespacedevs.com/2.2.0/event/upcoming"

# Космическая погода
SPACE_WEATHER_URL = "https://api.nasa.gov/DONKI/notifications"

# Google Custom Search API настройки
GOOGLE_API_KEY = "AIzaSyCAFlpSX41QY7KjOhSoTfy1nQYjpeT_pio"  # Получить на https://console.cloud.google.com/
GOOGLE_PROJECT_CX = "04bbc06e0b49b4697"    # Получить на https://programmablesearchengine.google.com/