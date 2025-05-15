import aiohttp
import datetime
import logging
from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.filters.magic_data import MagicData
from config import NASA_API_KEY, APOD_URL, NEO_URL, MARS_PHOTOS_URL, EARTH_URL
import keyboards
from aiogram.enums import ParseMode
from aiogram import F

# Настройка логирования
logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я космический бот NASA. Я могу показать вам:\n"
        "🌠 Астрономическое изображение дня (APOD)\n"
        "☄️ Информацию о приближающихся астероидах\n"
        "🔴 Фотографии с Марса\n"
        "🌍 Спутниковые снимки Земли\n"
        "🌞 Информацию о планетах Солнечной системы\n"
        "✨ Каталог экзопланет\n\n"
        "Используйте клавиатуру ниже для навигации:",
        reply_markup=keyboards.main_keyboard
    )

@router.message(F.text == "🌠 APOD")
async def get_apod(message: Message):
    async with aiohttp.ClientSession() as session:
        try:
            # Получаем вчерашнюю дату, так как NASA обновляет APOD обычно в течение дня
            yesterday = datetime.date.today() - datetime.timedelta(days=1)
            params = {
                "api_key": NASA_API_KEY,
                "date": yesterday.isoformat()
            }
            async with session.get(APOD_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Проверяем, является ли медиа видео или изображением
                    if data.get('media_type') == 'video':
                        caption = f"🌠 {data['title']}\n\n{data['explanation'][:1000]}..."
                        await message.answer(
                            f"{caption}\n\nВидео доступно по ссылке: {data['url']}",
                            reply_markup=keyboards.date_keyboard
                        )
                    else:  # image
                        caption = f"🌠 {data['title']}\n\n{data['explanation'][:1000]}..."
                        await message.answer_photo(
                            photo=data['url'],
                            caption=caption,
                            reply_markup=keyboards.date_keyboard
                        )
                else:
                    error_msg = f"Ошибка API: {response.status}"
                    logger.error(error_msg)
                    await message.answer(f"Извините, произошла ошибка при получении данных. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Ошибка при получении APOD: {str(e)}")
            await message.answer("Извините, произошла ошибка при получении данных. Попробуйте позже.")

@router.message(F.text == "☄️ Астероиды")
async def get_asteroids(message: Message):
    async with aiohttp.ClientSession() as session:
        params = {
            "api_key": NASA_API_KEY,
            "start_date": datetime.date.today().isoformat()
        }
        async with session.get(NEO_URL, params=params) as response:
            if response.status == 200:
                data = await response.json()
                asteroids = data['near_earth_objects'][datetime.date.today().isoformat()]
                
                text = "☄️ Околоземные астероиды на сегодня:\n\n"
                for ast in asteroids[:5]:  # Показываем только первые 5 астероидов
                    text += f"Название: {ast['name']}\n"
                    text += f"Размер: {ast['estimated_diameter']['meters']['estimated_diameter_min']:.1f}-{ast['estimated_diameter']['meters']['estimated_diameter_max']:.1f} м\n"
                    text += f"Опасен: {'Да' if ast['is_potentially_hazardous_asteroid'] else 'Нет'}\n\n"
                
                await message.answer(text)
            else:
                await message.answer("Извините, произошла ошибка при получении данных.")

@router.message(F.text == "🔴 Марс")
async def show_mars_options(message: Message):
    await message.answer(
        "Выберите марсоход для просмотра фотографий:",
        reply_markup=keyboards.mars_keyboard
    )

@router.callback_query(F.data.startswith("mars_"))
async def mars_photos(callback: CallbackQuery):
    rover = callback.data.split("_")[1]
    async with aiohttp.ClientSession() as session:
        try:
            # Разные sol для разных роверов с учетом их лучших периодов работы
            sols = {
                "curiosity": {"min": 3000, "max": 4000},    # Curiosity все еще активен
                "opportunity": {"min": 3000, "max": 4000},  # Самый продуктивный период Opportunity
                "perseverance": {"min": 100, "max": 800}    # Perseverance активен
            }
            
            import random
            rover_sols = sols.get(rover, {"min": 1000, "max": 2000})
            
            # Для получения разных фотографий делаем несколько попыток
            max_attempts = 5
            success = False
            
            for attempt in range(max_attempts):
                random_sol = random.randint(rover_sols["min"], rover_sols["max"])
                params = {
                    "api_key": NASA_API_KEY,
                    "sol": random_sol,
                    "page": random.randint(1, 3)  # Добавляем случайную страницу
                }
                
                url = MARS_PHOTOS_URL.format(rover)
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data['photos']:
                            # Берем случайное фото из всех доступных
                            photo = random.choice(data['photos'])
                            await callback.message.answer_photo(
                                photo=photo['img_src'],
                                caption=f"📸 Фото с марсохода {rover.capitalize()}\n"
                                        f"📅 Земная дата: {photo['earth_date']}\n"
                                        f"📍 Камера: {photo['camera']['full_name']}\n"
                                        f"🔢 Sol: {random_sol}"
                            )
                            success = True
                            break
            
            if not success:
                await callback.message.answer(f"Извините, не удалось найти фотографии для марсохода {rover}. Попробуйте еще раз.")
                
        except Exception as e:
            logger.error(f"Ошибка при получении фото с Марса: {str(e)}")
            await callback.message.answer("Извините, произошла ошибка при получении данных.")
            
    await callback.answer()

@router.message(F.text == "ℹ️ Помощь")
async def show_help(message: Message):
    await message.answer(
        "🚀 Команды бота:\n\n"
        "/start - Начать работу с ботом\n"
        "🌠 APOD - Астрономическое изображение дня\n"
        "☄️ Астероиды - Информация о околоземных астероидах\n"
        "🔴 Марс - Фотографии с марсоходов\n"
        "🌍 Земля - Спутниковые снимки Земли\n"
        "🌞 Солнечная система - Информация о планетах\n"
        "✨ Экзопланеты - Каталог известных экзопланет"
    )

@router.message(F.text == "🌍 Земля")
async def get_earth_imagery(message: Message):
    await message.answer("Пожалуйста, отправьте координаты места, которое хотите увидеть в формате: lat, lon\n"
                        "Например: 29.78, -95.33 (Хьюстон, США)")

@router.message(lambda message: message.text and ',' in message.text)
async def process_coordinates(message: Message):
    try:
        lat, lon = map(float, message.text.split(','))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Координаты вне допустимого диапазона")
        
        async with aiohttp.ClientSession() as session:
            params = {
                "api_key": NASA_API_KEY,
                "lat": lat,
                "lon": lon,
                "dim": 0.15,  # Размер изображения в градусах
                "date": datetime.date.today().isoformat()
            }
            async with session.get(EARTH_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'url' in data:
                        await message.answer_photo(
                            photo=data['url'],
                            caption=f"📍 Спутниковый снимок координат: {lat}, {lon}\n"
                                  f"📅 Дата съемки: {data.get('date', 'не указана')}"
                        )
                    else:
                        await message.answer("Извините, для этих координат нет доступных снимков.")
                else:
                    await message.answer("Произошла ошибка при получении снимка. Пожалуйста, попробуйте другие координаты.")
    except ValueError:
        await message.answer("Пожалуйста, введите координаты в правильном формате: latitude, longitude\n"
                           "Например: 29.78, -95.33")
    except Exception as e:
        await message.answer("Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.")

# Информация о планетах Солнечной системы
SOLAR_SYSTEM = {
    "sun": {
        "name": "☀️ Солнце",
        "type": "Звезда главной последовательности (жёлтый карлик)",
        "mass": "1.989 × 10^30 кг (333 000 масс Земли)",
        "diameter": "1 392 700 км",
        "temperature": "5 500°C (поверхность), 15 000 000°C (ядро)",
        "description": "Центральная звезда Солнечной системы, источник света и тепла для всех планет.",
        "image": "https://science.nasa.gov/wp-content/uploads/2023/09/sun.jpg"
    },    "mercury": {
        "name": "🌍 Меркурий",
        "type": "Планета земной группы",
        "mass": "3.285 × 10^23 кг",
        "orbit": "88 земных дней",
        "temperature": "-180°C до +430°C",
        "description": "Самая маленькая и ближайшая к Солнцу планета.",
        "image": "https://science.nasa.gov/wp-content/uploads/2023/09/mercury.jpg"
    },    "venus": {
        "name": "🌍 Венера",
        "type": "Планета земной группы",
        "mass": "4.867 × 10^24 кг",
        "diameter": "12 104 км",
        "temperature": "462°C (средняя)",
        "description": "Вторая планета от Солнца, названа в честь богини любви. Самая горячая планета системы.",
        "image": "https://science.nasa.gov/wp-content/uploads/2023/09/venus.jpg"
    },    "earth": {
        "name": "🌍 Земля",
        "type": "Планета земной группы",
        "mass": "5.972 × 10^24 кг",
        "diameter": "12 742 км",
        "temperature": "15°C (средняя)",
        "description": "Наша планета, единственная известная с жизнью. Третья от Солнца.",
        "image": "https://science.nasa.gov/wp-content/uploads/2023/09/earth.jpg"
    },    "mars": {
        "name": "🔴 Марс",
        "type": "Планета земной группы",
        "mass": "6.39 × 10^23 кг",
        "diameter": "6 779 км",
        "temperature": "-63°C (средняя)",
        "description": "Красная планета, четвёртая от Солнца. Имеет два спутника - Фобос и Деймос.",
        "image": "https://science.nasa.gov/wp-content/uploads/2023/09/mars.jpg"
    },    "jupiter": {
        "name": "🌟 Юпитер",
        "type": "Газовый гигант",
        "mass": "1.898 × 10^27 кг",
        "diameter": "139 820 км",
        "temperature": "-110°C (верхние слои)",
        "description": "Крупнейшая планета Солнечной системы. Имеет систему колец и множество спутников.",
        "image": "https://science.nasa.gov/wp-content/uploads/2023/09/jupiter.jpg"
    },    "saturn": {
        "name": "💫 Сатурн",
        "type": "Газовый гигант",
        "mass": "5.683 × 10^26 кг",
        "diameter": "116 460 км",
        "temperature": "-140°C (верхние слои)",
        "description": "Шестая планета от Солнца, известная своей впечатляющей системой колец.",
        "image": "https://science.nasa.gov/wp-content/uploads/2023/09/saturn.jpg"
    },    "uranus": {
        "name": "⭐ Уран",
        "type": "Ледяной гигант",
        "mass": "8.681 × 10^25 кг",
        "diameter": "50 724 км",
        "temperature": "-224°C (верхние слои)",
        "description": "Седьмая планета от Солнца, имеет необычный наклон оси вращения (98°).",
        "image": "https://science.nasa.gov/wp-content/uploads/2023/09/uranus.jpg"
    },    "neptune": {
        "name": "✨ Нептун",
        "type": "Ледяной гигант",
        "mass": "1.024 × 10^26 кг",
        "diameter": "49 244 км",
        "temperature": "-210°C (верхние слои)",
        "description": "Восьмая и самая дальняя планета, известная сильными ветрами в атмосфере.",
        "image": "https://science.nasa.gov/wp-content/uploads/2023/09/neptune.jpg"
    }
}

# Информация об экзопланетах
EXOPLANETS = {
    "proxima_b": {
        "name": "🌟 Proxima Centauri b",
        "distance": "4.2 световых года",
        "type": "Суперземля",
        "mass": "≥ 1.17 масс Земли",
        "year": "11.2 земных дней",
        "description": "Ближайшая известная экзопланета, находится в потенциально обитаемой зоне.",
        "image": "https://exoplanets.nasa.gov/system/resources/detail_files/2486_proximab_art2_1280.jpg"
    },    "trappist1_e": {
        "name": "✨ TRAPPIST-1 e",
        "distance": "39 световых лет",
        "type": "Землеподобная планета",
        "mass": "0.77 масс Земли",
        "year": "6.1 земных дней",
        "description": "Одна из семи планет системы TRAPPIST-1, считается наиболее похожей на Землю.",
        "image": "https://exoplanets.nasa.gov/system/resources/detail_files/2405_trappist-1e_1200.jpg"
    },    "kepler186f": {
        "name": "🌠 Kepler-186f",
        "distance": "582 световых года",
        "type": "Землеподобная планета",
        "mass": "1.2 масс Земли",
        "year": "130 земных дней",
        "description": "Первая обнаруженная экзопланета размером с Землю в обитаемой зоне.",
        "image": "https://exoplanets.nasa.gov/system/resources/detail_files/2406_kepler186f_1200.jpg"
    },    "hd40307g": {
        "name": "💫 HD 40307g",
        "distance": "42 световых года",
        "type": "Суперземля",
        "mass": "7.1 масс Земли",
        "year": "197.8 земных дней",
        "description": "Находится в обитаемой зоне своей звезды, потенциально может иметь жидкую воду.",
        "image": "https://exoplanets.nasa.gov/system/resources/detail_files/2534_superearth_1280.jpg"
    },    "toi700d": {
        "name": "⭐ TOI 700 d",
        "distance": "101.4 световых года",
        "type": "Землеподобная планета",
        "mass": "1.72 масс Земли",
        "year": "37 земных дней",
        "description": "Первая планета размером с Землю в обитаемой зоне, обнаруженная TESS.",
        "image": "https://exoplanets.nasa.gov/system/resources/detail_files/2634_TOI700d_1200.jpg"
    },    "k218b": {
        "name": "🌍 K2-18b",
        "distance": "124 световых года",
        "type": "Суперземля",
        "mass": "8.6 масс Земли",
        "year": "33 земных дня",
        "description": "Первая суперземля с подтвержденным наличием водяного пара в атмосфере.",
        "image": "https://exoplanets.nasa.gov/system/resources/detail_files/2422_K2-18-b_1200.jpg"
    },    "lhs1140b": {
        "name": "🌟 LHS 1140 b",
        "distance": "49 световых лет",
        "type": "Суперземля",
        "mass": "6.98 масс Земли",
        "year": "24.7 земных дней",
        "description": "Скалистая суперземля в обитаемой зоне, считается одним из лучших кандидатов для поиска жизни.",
        "image": "https://exoplanets.nasa.gov/system/resources/detail_files/2535_rocky_1280.jpg"
    },    "teegardenb": {
        "name": "✨ Teegarden b",
        "distance": "12.5 световых лет",
        "type": "Землеподобная планета",
        "mass": "1.05 масс Земли",
        "year": "4.9 земных дней",
        "description": "Одна из наиболее похожих на Землю экзопланет с индексом подобия 0.94.",
        "image": "https://exoplanets.nasa.gov/system/resources/detail_files/2533_earthlike_1280.jpg"
    }
}


@router.message(F.text == "🌞 Солнечная система")
async def show_planets(message: Message):
    await message.answer(
        "Выберите объект Солнечной системы для получения информации:",
        reply_markup=keyboards.planets_keyboard
    )

@router.message(F.text == "✨ Экзопланеты")
async def show_exoplanets(message: Message):
    await message.answer(
        "Выберите экзопланету для получения информации:",
        reply_markup=keyboards.exoplanets_keyboard
    )

@router.callback_query(F.data.startswith("planet_"))
async def planet_info(callback: CallbackQuery):
    planet_id = callback.data.split("_")[1]
    if planet_id in SOLAR_SYSTEM:
        planet = SOLAR_SYSTEM[planet_id]
        info = (f"{planet['name']}\n\n"
               f"🔹 Тип: {planet['type']}\n"
               f"🔹 Масса: {planet['mass']}\n"
               f"🔹 {'Диаметр' if 'diameter' in planet else 'Орбитальный период'}: "
               f"{planet.get('diameter', planet.get('orbit'))}\n"
               f"🔹 Температура: {planet['temperature']}\n\n"
               f"📝 {planet['description']}")
        
        # Отправляем фото с подписью
        await callback.message.answer_photo(
            photo=planet['image'],
            caption=info
        )
    await callback.answer()

@router.callback_query(F.data.startswith("exo_"))
async def exoplanet_info(callback: CallbackQuery):
    exo_id = "_".join(callback.data.split("_")[1:])
    if exo_id in EXOPLANETS:
        planet = EXOPLANETS[exo_id]
        info = (f"{planet['name']}\n\n"
               f"🔹 Расстояние от Земли: {planet['distance']}\n"
               f"🔹 Тип: {planet['type']}\n"
               f"🔹 Масса: {planet['mass']}\n"
               f"🔹 Год: {planet['year']}\n\n"
               f"📝 {planet['description']}")
        
        # Проверяем наличие изображения
        if 'image' in planet:
            await callback.message.answer_photo(
                photo=planet['image'],
                caption=info
            )
        else:
            await callback.message.answer(info)
    await callback.answer()