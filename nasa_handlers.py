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
                "thumbs": True
            }
            
            async with session.get(APOD_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('media_type') == 'video':
                        caption = f"🌠 {data.get('title', 'Astronomy Picture of the Day')}\n\n"
                        if 'explanation' in data:
                            caption += f"{data['explanation'][:1000]}..."
                        
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
                    
                    for ast in asteroids[:5]:
                        avg_size = (ast['estimated_diameter']['meters']['estimated_diameter_min'] + 
                                  ast['estimated_diameter']['meters']['estimated_diameter_max']) / 2
                        
                        if ast['is_potentially_hazardous_asteroid']:
                            img_url = "https://www.nasa.gov/wp-content/uploads/2019/04/hazardousasteroid.jpg"
                        elif avg_size >= 500:
                            img_url = "https://www.nasa.gov/wp-content/uploads/2019/04/largeasteroid.jpg"
                        elif avg_size >= 100:
                            img_url = "https://www.nasa.gov/wp-content/uploads/2019/04/mediumasteroid.jpg"
                        else:
                            img_url = "https://www.nasa.gov/wp-content/uploads/2019/04/smallasteroid.jpg"
                        
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
                            await message.answer(text)
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
                good_sols = [
                    100, 200, 300, 400, 500, 600,
                    700, 800, 900, 1000, 1100, 1200
                ]
                params = {
                    "api_key": NASA_API_KEY,
                    "sol": random.choice(good_sols),
                    "camera": "PANCAM",
                    "page": 1
                }
            else:
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
                        if rover == "opportunity":
                            params["camera"] = "NAVCAM"
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
                "dim": 0.15,
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

@router.callback_query(F.data == "main_menu")
async def return_to_main_menu(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите интересующий вас раздел:",
        reply_markup=keyboards.main_keyboard
    )
    await callback.answer()
