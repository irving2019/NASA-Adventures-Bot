"""
Модуль обработчиков команд для взаимодействия с API NASA.

Этот модуль содержит обработчики для различных команд, связанных с получением
данных от NASA API, включая:
- Астрономическое изображение дня (APOD)
- Информацию о околоземных астероидах
- Фотографии с марсоходов
- Спутниковые снимки Земли

Attributes:
    router (Router): Роутер для обработки команд, связанных с NASA API
    logger (Logger): Логгер для записи событий модуля
"""

import logging
from datetime import date, datetime
import random
from typing import Dict, List, Optional, Union, Any

import aiohttp
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import URLInputFile

from config import NASA_API_KEY, APOD_URL, NEO_URL, MARS_PHOTOS_URL, EARTH_URL
import keyboards


logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """
    Обработчик команды /start.
    
    Отправляет приветственное сообщение и показывает основную клавиатуру с доступными командами.
    
    Args:
        message (Message): Входящее сообщение от пользователя
        
    Returns:
        None
    """
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
async def get_apod(message: Message) -> None:
    """
    Обработчик команды получения астрономического изображения дня.
    
    Отправляет пользователю изображение или видео дня от NASA с описанием.
    Поддерживает как статические изображения, так и видео контент.
    
    Args:
        message (Message): Входящее сообщение от пользователя
        
    Returns:
        None
    """
    async with aiohttp.ClientSession() as session:
        try:
            params: Dict[str, Union[str, bool]] = {
                "api_key": NASA_API_KEY,
                "thumbs": True
            }
            
            async with session.get(APOD_URL, params=params) as response:
                if response.status == 200:
                    data: Dict[str, Any] = await response.json()
                    
                    if data.get('media_type') == 'video':
                        caption = f"🌠 {data.get('title', 'Astronomy Picture of the Day')}\n\n"
                        if 'explanation' in data:
                            caption += f"{data['explanation'][:1000]}..."
                        
                        if data.get('thumbnail_url'):
                            await message.answer_photo(
                                photo=URLInputFile(data['thumbnail_url']),
                                caption=f"{caption}\n\n🎥 Видео доступно по ссылке: {data['url']}"
                            )
                        else:
                            await message.answer(
                                f"{caption}\n\n🎥 Видео доступно по ссылке: {data['url']}"
                            )
                    else:
                        caption = f"🌠 {data.get('title', 'Astronomy Picture of the Day')}\n\n"
                        if 'explanation' in data:
                            caption += data['explanation']
                        
                        await message.answer_photo(
                            photo=URLInputFile(data['url']),
                            caption=caption
                        )
                else:
                    logger.error(f"Ошибка при получении APOD: {response.status}")
                    await message.answer("Извините, произошла ошибка при получении изображения дня. Попробуйте позже.")
                    
        except Exception as e:
            logger.error(f"Ошибка при получении APOD: {e}")
            await message.answer("Извините, произошла ошибка при получении изображения дня. Попробуйте позже.")

@router.message(F.text == "☄️ Астероиды")
async def get_asteroids(message: Message) -> None:
    """
    Обработчик команды получения информации о приближающихся астероидах.
    
    Получает данные о околоземных астероидах на текущую дату и отправляет
    информацию о наиболее близких и потенциально опасных объектах.
    
    Args:
        message (Message): Входящее сообщение от пользователя
        
    Returns:
        None
    """
    async with aiohttp.ClientSession() as session:
        try:
            today = date.today().isoformat()
            params: Dict[str, str] = {
                "api_key": NASA_API_KEY,
                "start_date": today,
                "end_date": today
            }
            
            async with session.get(NEO_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    today = date.today().isoformat()
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
async def get_mars_photos(message: Message) -> None:
    """
    Обработчик команды получения фотографий с Марса.
    
    Получает случайную фотографию с одного из действующих марсоходов (Curiosity, Perseverance)
    и отправляет её пользователю вместе с информацией о дате съемки и камере.
    
    Args:
        message (Message): Входящее сообщение от пользователя
        
    Returns:
        None
    """
    rovers: List[str] = ["curiosity", "perseverance"]
    rover: str = random.choice(rovers)
    
    async with aiohttp.ClientSession() as session:
        try:
            params: Dict[str, str] = {
                "api_key": NASA_API_KEY,
                "sol": "1000"  # Примерно середина миссии для получения хороших фото
            }
            
            url: str = MARS_PHOTOS_URL.format(rover)
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data: Dict[str, Any] = await response.json()
                    
                    if photos := data.get('photos', []):
                        photo = random.choice(photos)
                        
                        caption = (
                            f"📸 Фото с марсохода {photo['rover']['name']}\n"
                            f"📅 Дата съёмки: {photo['earth_date']}\n"
                            f"🎥 Камера: {photo['camera']['full_name']}"
                        )
                        
                        await message.answer_photo(
                            photo=URLInputFile(photo['img_src']),
                            caption=caption,
                            reply_markup=keyboards.get_mars_photos_keyboard()
                        )
                    else:
                        await message.answer("К сожалению, фотографии не найдены. Попробуйте позже.")
                else:
                    logger.error(f"Ошибка при получении фото с Марса: {response.status}")
                    await message.answer("Извините, произошла ошибка при получении фотографий. Попробуйте позже.")
                    
        except Exception as e:
            logger.error(f"Ошибка при получении фото с Марса: {e}")
            await message.answer("Извините, произошла ошибка при получении фотографий. Попробуйте позже.")

@router.message(F.text == "ℹ️ Помощь")
async def show_help(message: Message) -> None:
    """
    Обработчик команды помощи.
    
    Отправляет пользователю список доступных команд и их описание.
    
    Args:
        message (Message): Входящее сообщение от пользователя
        
    Returns:
        None
    """
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
async def get_earth_image(message: Message) -> None:
    """
    Обработчик команды получения спутниковых снимков Земли.
    
    Запрашивает у пользователя координаты и отправляет спутниковый снимок
    указанной локации с NASA Earth API.
    
    Args:
        message (Message): Входящее сообщение от пользователя
        
    Returns:
        None
    """
    await message.answer(
        "Для получения спутникового снимка, отправьте мне координаты в формате:\n"
        "latitude,longitude\n\n"
        "Например: 55.7558,37.6173 (Москва)",
        reply_markup=keyboards.get_back_keyboard()
    )

@router.message(F.text.regexp(r'^-?\d+\.?\d*,-?\d+\.?\d*$'))
async def process_coordinates(message: Message) -> None:
    """
    Обработчик получения координат для спутникового снимка.
    
    Получает координаты от пользователя, валидирует их, запрашивает спутниковый снимок
    этой локации из NASA Earth API и отправляет его пользователю.
    
    Args:
        message (Message): Входящее сообщение с координатами
        
    Returns:
        None
        
    Note:
        Координаты должны быть в формате "latitude,longitude",
        где latitude: [-90, 90], longitude: [-180, 180]
    """
    try:
        lat, lon = map(float, message.text.split(','))
        
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            await message.answer(
                "Некорректные координаты! Широта должна быть от -90 до 90, долгота от -180 до 180."
            )
            return
        
        async with aiohttp.ClientSession() as session:
            params: Dict[str, Union[str, float]] = {
                "api_key": NASA_API_KEY,
                "lat": lat,
                "lon": lon,
                "dim": 0.3,  # Размер области в градусах
                "date": date.today().isoformat()
            }
            
            async with session.get(EARTH_URL, params=params) as response:
                if response.status == 200:
                    image_data = await response.read()
                    
                    caption = f"🌍 Спутниковый снимок локации: {lat}, {lon}"
                    
                    await message.answer_photo(
                        photo=image_data,
                        caption=caption,
                        reply_markup=keyboards.get_back_keyboard()
                    )
                else:
                    logger.error(f"Ошибка при получении снимка Земли: {response.status}")
                    await message.answer(
                        "Извините, не удалось получить снимок для этой локации. "
                        "Возможно, для неё нет доступных данных."
                    )
                    
    except ValueError:
        await message.answer(
            "Неверный формат координат. Пожалуйста, используйте формат: latitude,longitude\n"
            "Например: 55.7558,37.6173"
        )
    except Exception as e:
        logger.error(f"Ошибка при получении снимка Земли: {e}")
        await message.answer("Извините, произошла ошибка при получении снимка. Попробуйте позже.")

@router.callback_query(F.data == "main_menu")
async def return_to_main_menu(callback: CallbackQuery) -> None:
    """
    Обработчик команды возврата в главное меню.
    
    Показывает пользователю главное меню с основными командами бота.
    
    Args:
        callback (CallbackQuery): Входящий колбек от пользователя
        
    Returns:
        None
    """
    await callback.message.answer(
        "Выберите интересующий вас раздел:",
        reply_markup=keyboards.main_keyboard
    )
    await callback.answer()
