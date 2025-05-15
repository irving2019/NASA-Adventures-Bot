import aiohttp
import datetime
import logging
import random
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
            params = {
                "api_key": NASA_API_KEY,
                "thumbs": True  # Запрашиваем миниатюры для видео
            }
            
            async with session.get(APOD_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Проверяем тип медиа
                    if data.get('media_type') == 'video':
                        caption = f"🌠 {data.get('title', 'Astronomy Picture of the Day')}\n\n"
                        if 'explanation' in data:
                            caption += f"{data['explanation'][:1000]}..."
                        
                        # Если есть миниатюра, отправляем её с ссылкой на видео
                        if data.get('thumbnail_url'):
                            await message.answer_photo(
                                photo=data['thumbnail_url'],
                                caption=f"{caption}\n\n🎥 Видео доступно по ссылке: {data['url']}",
                                reply_markup=keyboards.date_keyboard
                            )
                        else:
                            await message.answer(
                                f"{caption}\n\n🎥 Видео доступно по ссылке: {data['url']}",
                                reply_markup=keyboards.date_keyboard
                            )
                    else:  # image
                        caption = f"🌠 {data.get('title', 'Astronomy Picture of the Day')}\n\n"
                        if 'explanation' in data:
                            caption += f"{data['explanation'][:1000]}..."
                        
                        try:
                            await message.answer_photo(
                                photo=data['url'],
                                caption=caption,
                                reply_markup=keyboards.date_keyboard
                            )
                        except Exception as img_error:
                            logger.error(f"Ошибка при отправке изображения APOD: {str(img_error)}")
                            await message.answer(
                                f"{caption}\n\n🔗 Изображение доступно по ссылке: {data['url']}",
                                reply_markup=keyboards.date_keyboard
                            )
                else:
                    logger.error(f"Ошибка API NASA (APOD): {response.status}")
                    await message.answer("Извините, произошла ошибка при получении данных. Попробуйте позже.")
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
        try:
            async with session.get(NEO_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    today = datetime.date.today().isoformat()
                    asteroids = data['near_earth_objects'].get(today, [])
                    
                    if not asteroids:
                        await message.answer("На сегодня нет данных об астероидах. Попробуйте позже.")
                        return
                    
                    # Отправляем информацию о каждом астероиде
                    for ast in asteroids[:5]:  # Показываем только первые 5 астероидов
                        # Определяем размер астероида
                        avg_size = (ast['estimated_diameter']['meters']['estimated_diameter_min'] + 
                                  ast['estimated_diameter']['meters']['estimated_diameter_max']) / 2
                        
                        # Выбираем иллюстрацию в зависимости от размера и опасности
                        if ast['is_potentially_hazardous_asteroid']:
                            img_url = "https://www.nasa.gov/wp-content/uploads/2019/04/hazardousasteroid.jpg"
                        elif avg_size >= 500:
                            img_url = "https://www.nasa.gov/wp-content/uploads/2019/04/largeasteroid.jpg"
                        elif avg_size >= 100:
                            img_url = "https://www.nasa.gov/wp-content/uploads/2019/04/mediumasteroid.jpg"
                        else:
                            img_url = "https://www.nasa.gov/wp-content/uploads/2019/04/smallasteroid.jpg"
                        
                        # Формируем текст описания
                        text = (f"☄️ Астероид: {ast['name']}\n\n"
                               f"📏 Размер: {ast['estimated_diameter']['meters']['estimated_diameter_min']:.1f}"
                               f"-{ast['estimated_diameter']['meters']['estimated_diameter_max']:.1f} м\n"
                               f"⚠️ Опасен: {'Да ☢️' if ast['is_potentially_hazardous_asteroid'] else 'Нет ✅'}\n"
                               f"🔺 Макс. сближение: {float(ast['close_approach_data'][0]['miss_distance']['kilometers']):.0f} км\n"
                               f"🚀 Относительная скорость: {float(ast['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']):.0f} км/ч\n"
                               f"⏰ Время макс. сближения: {ast['close_approach_data'][0]['close_approach_date_full']}")
                        
                        try:
                            await message.answer_photo(
                                photo=img_url,
                                caption=text,
                                parse_mode="HTML"
                            )
                        except Exception as img_error:
                            logger.error(f"Ошибка при отправке фото астероида: {str(img_error)}")
                            await message.answer(text)  # Отправляем только текст, если с фото проблема
                else:
                    logger.error(f"Ошибка API NASA (NEO): {response.status}")
                    await message.answer("Извините, произошла ошибка при получении данных об астероидах.")
        except Exception as e:
            logger.error(f"Ошибка при получении данных об астероидах: {str(e)}")
            await message.answer("Произошла ошибка при получении данных об астероидах. Попробуйте позже.")

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
            # Определяем параметры для Opportunity
            if rover == "opportunity":
                # Известные рабочие sols для Opportunity
                good_sols = [
                    100, 200, 300, 400, 500, 600,
                    700, 800, 900, 1000, 1100, 1200
                ]
                params = {
                    "api_key": NASA_API_KEY,
                    "sol": random.choice(good_sols),
                    "camera": "PANCAM",  # Используем основную научную камеру
                    "page": 1
                }
            else:
                # Параметры для других марсоходов
                sols = {
                    "curiosity": {"min": 3000, "max": 4000},
                    "perseverance": {"min": 100, "max": 800}
                }
                rover_sols = sols.get(rover, {"min": 1000, "max": 2000})
                params = {
                    "api_key": NASA_API_KEY,
                    "sol": random.randint(rover_sols["min"], rover_sols["max"]),
                    "page": random.randint(1, 3)
                }

            # Делаем запрос к API
            url = MARS_PHOTOS_URL.format(rover)
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['photos']:
                        photo = random.choice(data['photos'])
                        await callback.message.answer_photo(
                            photo=photo['img_src'],
                            caption=(f"📸 Фото с марсохода {rover.capitalize()}\n"
                                   f"📅 Земная дата: {photo['earth_date']}\n"
                                   f"📍 Камера: {photo['camera']['full_name']}\n"
                                   f"🔢 Sol: {params['sol']}")
                        )
                    else:
                        # Если фотографии не найдены, пробуем другие параметры для Opportunity
                        if rover == "opportunity":
                            params["camera"] = "NAVCAM"  # Пробуем другую камеру
                            async with session.get(url, params=params) as retry_response:
                                if retry_response.status == 200:
                                    retry_data = await retry_response.json()
                                    if retry_data['photos']:
                                        photo = random.choice(retry_data['photos'])
                                        await callback.message.answer_photo(
                                            photo=photo['img_src'],
                                            caption=(f"📸 Фото с марсохода {rover.capitalize()}\n"
                                                   f"📅 Земная дата: {photo['earth_date']}\n"
                                                   f"📍 Камера: {photo['camera']['full_name']}\n"
                                                   f"🔢 Sol: {params['sol']}")
                                        )
                                    else:
                                        await callback.message.answer(
                                            f"Извините, не удалось найти фотографии для марсохода {rover}. "
                                            f"Попробуйте еще раз."
                                        )
                        else:
                            await callback.message.answer(
                                f"Извините, не удалось найти фотографии для марсохода {rover}. "
                                f"Попробуйте еще раз."
                            )
                else:
                    logger.error(f"Ошибка API NASA: {response.status}")
                    await callback.message.answer(
                        "Извините, произошла ошибка при получении данных. Попробуйте позже."
                    )
        except Exception as e:
            logger.error(f"Ошибка при получении фото с Марса: {str(e)}")
            await callback.message.answer(
                "Извините, произошла ошибка при получении данных. Попробуйте позже."
            )
    
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
SOLAR_SYSTEM = {    "sun": {
        "name": "☀️ Солнце",
        "type": "Звезда главной последовательности (жёлтый карлик)",
        "mass": "1.989 × 10^30 кг (333 000 масс Земли)",
        "diameter": "1 392 700 км",
        "temperature": "5 500°C (поверхность), 15 000 000°C (ядро)",
        "description": "Центральная звезда Солнечной системы, источник света и тепла для всех планет.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4/The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg/1280px-The_Sun_by_the_Atmospheric_Imaging_Assembly_of_NASA%27s_Solar_Dynamics_Observatory_-_20100819.jpg"
    },    "mercury": {
        "name": "🌍 Меркурий",
        "type": "Планета земной группы",
        "mass": "3.285 × 10^23 кг",
        "orbit": "88 земных дней",
        "temperature": "-180°C до +430°C",
        "description": "Самая маленькая и ближайшая к Солнцу планета.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Mercury_in_color_-_Prockter07_centered.jpg/1280px-Mercury_in_color_-_Prockter07_centered.jpg"
    },
    "venus": {
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
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97/The_Earth_seen_from_Apollo_17.jpg/1280px-The_Earth_seen_from_Apollo_17.jpg"
    },
    "mars": {
        "name": "🔴 Марс",
        "type": "Планета земной группы",
        "mass": "6.39 × 10^23 кг",
        "diameter": "6 779 км",
        "temperature": "-63°C (средняя)",
        "description": "Красная планета, четвёртая от Солнца. Имеет два спутника - Фобос и Деймос.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/OSIRIS_Mars_true_color.jpg/1280px-OSIRIS_Mars_true_color.jpg"
    },
    "jupiter": {
        "name": "🌟 Юпитер",
        "type": "Газовый гигант",
        "mass": "1.898 × 10^27 кг",
        "diameter": "139 820 км",
        "temperature": "-110°C (верхние слои)",
        "description": "Крупнейшая планета Солнечной системы. Имеет систему колец и множество спутников.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/1280px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg"
    },    "saturn": {
        "name": "💫 Сатурн",
        "type": "Газовый гигант",
        "mass": "5.683 × 10^26 кг",
        "diameter": "116 460 км",
        "temperature": "-140°C (верхние слои)",
        "description": "Шестая планета от Солнца, известная своей впечатляющей системой колец.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Saturn_during_Equinox.jpg/1280px-Saturn_during_Equinox.jpg"
    },
    "uranus": {
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
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg/1280px-Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg"
    }
}

# Информация об экзопланетах (отсортированы по индексу землеподобия - ESI)
EXOPLANETS = {
    "teegardenb": {
        "name": "1️⃣ Teegarden b (ESI: 0.95)",
        "distance": "12.5 световых лет",
        "type": "Землеподобная планета",
        "mass": "1.05 масс Земли",
        "year": "4.9 земных дней",
        "star": "Teegarden (ультрахолодный карлик)",
        "description": "Самая похожая на Землю экзопланета с индексом подобия 0.95. Температура поверхности близка к земной.",
        "image": "https://www.uzaygo.com/wp-content/uploads/2021/12/Teegarden-B-gezegeni.jpg"
    },
    "kepler442b": {
        "name": "2️⃣ Kepler-442b (ESI: 0.84)",
        "distance": "1,206 световых лет",
        "type": "Суперземля",
        "mass": "2.36 масс Земли",
        "year": "112.3 земных дней",
        "star": "Kepler-442 (оранжевый карлик)",
        "description": "Одна из наиболее перспективных экзопланет для поиска жизни с высоким индексом землеподобия.",
        "image": "https://exoplanets.nasa.gov/system/resources/detail_files/2207_kepler442b_art2_1280.jpg"
    },
    "trappist1_e": {
        "name": "3️⃣ TRAPPIST-1e (ESI: 0.82)",
        "distance": "39 световых лет",
        "type": "Скалистая планета",
        "mass": "0.77 масс Земли",
        "year": "6.1 земных дней",
        "star": "TRAPPIST-1 (ультрахолодный карлик)",
        "description": "Третья по схожести с Землей экзопланета. Имеет схожие размеры и получает примерно столько же энергии от своей звезды, как Земля от Солнца.",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/TRAPPIST-1_Planet-f.jpg/640px-TRAPPIST-1_Planet-f.jpg"
    },
    "kepler186f": {
        "name": "4️⃣ Kepler-186f (ESI: 0.79)",
        "distance": "582 световых года",
        "type": "Землеподобная планета",
        "mass": "~1.2 масс Земли",
        "year": "130 земных дней",
        "star": "Kepler-186 (красный карлик)",
        "description": "Первая открытая землеподобная планета в обитаемой зоне. Размер планеты всего на 10% больше Земли.",
        "image": "https://www.cnet.com/a/img/resize/5fd1399118a844fa5605d0f071209ab9dc20f48c/hub/2014/04/17/4e7441aa-945c-4f78-92e8-99bcf2582f08/kepler186f.jpg?auto=webp&width=1200"
    },
    "proxima_b": {
        "name": "5️⃣ Proxima Centauri b (ESI: 0.75)",
        "distance": "4.2 световых года",
        "type": "Суперземля",
        "mass": "≥ 1.17 масс Земли",
        "year": "11.2 земных дней",
        "star": "Proxima Centauri (красный карлик)",
        "description": "Ближайшая к Земле экзопланета с высоким индексом землеподобия, находится в потенциально обитаемой зоне.",
        "image": "https://orbitaltoday.com/wp-content/uploads/2023/03/Proxima-b-.jpg"
    },
    "kepler452b": {
        "name": "6️⃣ Kepler-452b (ESI: 0.72)",
        "distance": "1,402 световых года",
        "type": "Суперземля",
        "mass": "5 масс Земли",
        "year": "385 земных дней",
        "star": "Kepler-452 (жёлтый карлик, похож на Солнце)",
        "description": "Известна как 'Земля 2.0'. Вращается вокруг звезды, очень похожей на наше Солнце, с периодом близким к земному году.",
        "image": "https://www.nasa.gov/wp-content/uploads/2015/07/452b_artist_concept.jpg"
    },
    "kepler62f": {
        "name": "7️⃣ Kepler-62f (ESI: 0.67)",
        "distance": "1,200 световых лет",
        "type": "Суперземля",
        "mass": "2.8 масс Земли",
        "year": "267 земных дней",
        "star": "Kepler-62 (оранжевый карлик)",
        "description": "Потенциально океаническая планета в обитаемой зоне. Может быть полностью покрыта глубоким океаном.",
        "image": "https://www.nasa.gov/wp-content/uploads/2013/04/kepler62f_1.jpg"
    },
    "toi700d": {
        "name": "8️⃣ TOI-700d (ESI: 0.65)",
        "distance": "101.4 световых года",
        "type": "Землеподобная планета",
        "mass": "1.72 масс Земли",
        "year": "37 земных дней",
        "star": "TOI-700 (красный карлик)",
        "description": "Одна из первых планет размером с Землю в обитаемой зоне, открытая телескопом TESS.",
        "image": "https://www.nasa.gov/wp-content/uploads/2020/01/toi700d-concept-2.jpg"
    },
    "lhs1140b": {
        "name": "9️⃣ LHS 1140b (ESI: 0.63)",
        "distance": "49 световых лет",
        "type": "Суперземля",
        "mass": "6.98 масс Земли",
        "year": "24.7 земных дней",
        "star": "LHS 1140 (красный карлик)",
        "description": "Массивная скалистая планета в обитаемой зоне. Плотная атмосфера может защищать поверхность от радиации.",
        "image": "https://www.eso.org/public/archives/images/screen/ann17049a.jpg"
    },
    "k218b": {
        "name": "🔟 K2-18b (ESI: 0.61)",
        "distance": "124 световых года",
        "type": "Суперземля",
        "mass": "8.6 масс Земли",
        "year": "33 земных дня",
        "star": "K2-18 (красный карлик)",
        "description": "Первая суперземля с подтвержденным наличием водяного пара в атмосфере. Находится в обитаемой зоне.",
        "image": "https://www.eso.org/public/archives/images/screen/K2-18b_concept.jpg"
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
        "Топ 10 экзопланет по коэффициенту землеподобности 🌎\n"
        "Отсортированы по ESI (Earth Similarity Index) от самых похожих на Землю",
        reply_markup=keyboards.exoplanets_keyboard
    )

@router.callback_query(F.data.startswith("planet_"))
async def planet_info(callback: CallbackQuery):
    try:
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
            
            try:
                # Отправляем фото с подписью
                await callback.message.answer_photo(
                    photo=planet['image'],
                    caption=info
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке фото планеты {planet_id}: {str(e)}")
                # Если не удалось отправить фото, отправляем только текст
                await callback.message.answer(info)
        else:
            logger.error(f"Планета {planet_id} не найдена в базе данных")
            await callback.message.answer("Извините, информация о данном объекте временно недоступна")
    except Exception as e:
        logger.error(f"Ошибка при обработке информации о планете: {str(e)}")
        await callback.message.answer("Произошла ошибка при получении информации. Попробуйте позже.")
    
    await callback.answer()

@router.callback_query(F.data.startswith("exo_"))
async def exoplanet_info(callback: CallbackQuery):
    try:
        exo_id = "_".join(callback.data.split("_")[1:])
        if exo_id in EXOPLANETS:
            planet = EXOPLANETS[exo_id]
            info = (f"{planet['name']}\n\n"
                   f"🔹 Расстояние от Земли: {planet['distance']}\n"
                   f"🌟 Родительская звезда: {planet['star']}\n"
                   f"🔹 Тип: {planet['type']}\n"
                   f"🔹 Масса: {planet['mass']}\n"
                   f"🔹 Год: {planet['year']}\n\n"
                   f"📝 {planet['description']}")
            
            try:                # Проверяем наличие изображения и пытаемся его отправить
                if 'image' in planet and planet['image']:
                    try:
                        async with aiohttp.ClientSession() as session:
                            async with session.get(planet['image']) as response:
                                if response.status == 200:
                                    await callback.message.answer_photo(
                                        photo=planet['image'],
                                        caption=info
                                    )
                                else:
                                    logger.error(f"Ошибка загрузки изображения для {exo_id}, статус: {response.status}")
                                    await callback.message.answer(info)
                    except Exception as img_error:
                        logger.error(f"Ошибка при проверке изображения для {exo_id}: {str(img_error)}")
                        await callback.message.answer(info)
                else:
                    await callback.message.answer(info)
            except Exception as e:
                logger.error(f"Ошибка при отправке фото экзопланеты {exo_id}: {str(e)}")
                await callback.message.answer(info)
        else:
            logger.error(f"Экзопланета {exo_id} не найдена в базе данных")
            await callback.message.answer("Извините, информация о данной экзопланете временно недоступна")
    except Exception as e:
        logger.error(f"Ошибка при обработке информации об экзопланете: {str(e)}")
        await callback.message.answer("Произошла ошибка при получении информации. Попробуйте позже.")
    
    await callback.answer()

async def send_planet_info(callback: CallbackQuery, planet_data: dict):
    try:
        info = f"{planet_data['name']}\n\n"
        info += f"📏 Расстояние: {planet_data['distance']}\n"
        info += f"🌍 Тип: {planet_data['type']}\n"
        info += f"⚖️ Масса: {planet_data['mass']}\n"
        info += f"🕒 Год: {planet_data['year']}\n\n"
        info += f"ℹ️ {planet_data['description']}"

        try:
            await callback.message.answer_photo(
                photo=planet_data['image'],
                caption=info,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Ошибка при загрузке изображения: {str(e)}")
            # Отправляем сообщение без изображения в случае ошибки
            await callback.message.answer(
                text=f"❌ Извините, изображение недоступно.\n\n{info}",
                parse_mode='HTML'
            )
            
        await callback.answer()
    except Exception as e:
        logger.error(f"Общая ошибка при отправке информации: {str(e)}")
        await callback.message.answer("❌ Произошла ошибка при получении информации о планете.")
        await callback.answer()

@router.callback_query(F.data == "main_menu")
async def return_to_main_menu(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите интересующий вас раздел:",
        reply_markup=keyboards.main_keyboard
    )
    await callback.answer()