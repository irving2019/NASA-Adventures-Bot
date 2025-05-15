import aiohttp
import datetime
import logging
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from config import NASA_API_KEY, APOD_URL, NEO_URL, MARS_PHOTOS_URL, EARTH_URL
import keyboards

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
        "🌍 Спутниковые снимки Земли\n\n"
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
        "🌍 Земля - Спутниковые снимки Земли"
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