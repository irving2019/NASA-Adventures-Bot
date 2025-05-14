# NASA Adventures Bot 🚀

Телеграм-бот для исследования космоса с помощью API NASA. Бот предоставляет доступ к различным космическим данным и изображениям.

## Возможности 🌟

- 🌠 **APOD (Astronomy Picture of the Day)**: Получение астрономического изображения дня с описанием
- ☄️ **Астероиды**: Информация о околоземных астероидах в реальном времени
- 🔴 **Фотографии Марса**: Снимки с марсоходов (Curiosity, Perseverance, Opportunity)
- 🌍 **Спутниковые снимки Земли**: Просмотр спутниковых снимков по координатам

## Установка и настройка 🛠

### Предварительные требования

- Python 3.8 или выше
- Токен Telegram бота (получить у [@BotFather](https://t.me/BotFather))
- API ключ NASA (получить на [api.nasa.gov](https://api.nasa.gov/))

### Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/your-username/nasa-adventures-bot.git
cd nasa-adventures-bot
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
.\venv\Scripts\activate  # для Windows
source venv/bin/activate  # для Linux/Mac
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `config.py` со следующим содержимым:
```python
# Токен для Telegram бота
TOKEN = "ВАШ_ТЕЛЕГРАМ_ТОКЕН"

# API ключ NASA
NASA_API_KEY = "ВАШ_API_КЛЮЧ_NASA"

# URLs для API NASA
APOD_URL = "https://api.nasa.gov/planetary/apod"
NEO_URL = "https://api.nasa.gov/neo/rest/v1/feed"
MARS_PHOTOS_URL = "https://api.nasa.gov/mars-photos/api/v1/rovers/{}/photos"
EARTH_URL = "https://api.nasa.gov/planetary/earth/assets"
```

### Получение API ключа NASA

1. Перейдите на сайт [api.nasa.gov](https://api.nasa.gov/)
2. Прокрутите до формы "Generate API Key"
3. Заполните форму:
   - First Name: Ваше имя
   - Last Name: Ваша фамилия
   - Email: Ваш email
   - Organization: Необязательно
4. Нажмите "Signup"
5. Вы получите API ключ на указанный email

### Запуск бота

1. Убедитесь, что виртуальное окружение активировано
2. Запустите бота:
```bash
python run.py
```

## Использование 🎮

1. Найдите вашего бота в Telegram по имени, которое вы задали в @BotFather
2. Отправьте команду `/start`
3. Используйте кнопки меню для навигации:
   - 🌠 APOD - для просмотра астрономического изображения дня
   - ☄️ Астероиды - для получения информации о околоземных астероидах
   - 🔴 Марс - для просмотра фотографий с марсоходов
   - 🌍 Земля - для получения спутниковых снимков (требуется ввод координат)

## Вклад в проект 🤝

Pull requests приветствуются. Для крупных изменений, пожалуйста, сначала создайте issue для обсуждения предлагаемых изменений.

## Лицензия 📝

[MIT](https://choosealicense.com/licenses/mit/)
