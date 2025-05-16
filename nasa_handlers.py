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

import asyncio
import logging
from datetime import date, datetime
import random
from utils.monitoring import track_performance, monitor
from typing import Dict, List, Optional, Union, Any
from io import BytesIO
from PIL import Image

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import BufferedInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramForbiddenError

from config import NASA_API_KEY, APOD_URL, NEO_URL, MARS_PHOTOS_URL, EARTH_URL
import keyboards
from utils.cache import cache_response
from utils.http import nasa_client, neo_client, earth_client


logger = logging.getLogger(__name__)
router = Router()

# Константы
MAX_IMAGE_SIZE = (1280, 1280)  # Максимальный размер изображения
CACHE_TIME = 3600  # Время кэширования в секундах

async def optimize_image(image_data: bytes) -> bytes:
    """
    Оптимизирует размер изображения для быстрой отправки.
    
    Args:
        image_data (bytes): Исходные данные изображения
        
    Returns:
        bytes: Оптимизированные данные изображения
    """
    try:
        with Image.open(BytesIO(image_data)) as img:
            # Проверяем, нужно ли оптимизировать
            if img.size[0] <= MAX_IMAGE_SIZE[0] and img.size[1] <= MAX_IMAGE_SIZE[1]:
                return image_data
                
            # Изменяем размер с сохранением пропорций
            img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
            
            # Сохраняем оптимизированное изображение
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=85, optimize=True)
            return buffer.getvalue()
    except Exception as e:
        logger.error(f"Ошибка при оптимизации изображения: {e}")
        return image_data  # Возвращаем оригинал в случае ошибки

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start."""
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
@track_performance()
@cache_response(cache_type='apod')
async def get_apod(message: Message) -> None:
    """Обработчик команды APOD."""
    logger.info("Обработчик APOD вызван")
    try:
        params = {"api_key": NASA_API_KEY, "thumbs": True}
        logger.info(f"Параметры запроса: {params}")
        data = await nasa_client.get("/planetary/apod", params=params)
        logger.info(f"Ответ API: {data}")
        
        if data.get('media_type') == 'video':
            caption = f"🌠 {data.get('title', 'Astronomy Picture of the Day')}\n\n"
            if 'explanation' in data:
                caption += f"{data['explanation'][:1000]}..."
            
            if thumbnail_url := data.get('thumbnail_url'):
                image_data = await nasa_client.get_bytes(thumbnail_url)
                optimized_image = await optimize_image(image_data)
                
                await message.answer_photo(
                    photo=BufferedInputFile(optimized_image, "apod_thumb.jpg"),
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
            
            image_data = await nasa_client.get_bytes(data['url'])
            optimized_image = await optimize_image(image_data)
            
            await message.answer_photo(
                photo=BufferedInputFile(optimized_image, "apod.jpg"),
                caption=caption
            )
            
    except Exception as e:
        logger.error(f"Ошибка при получении APOD: {e}")

@router.message(F.text == "☄️ Астероиды")
@track_performance()
@cache_response(cache_type='asteroids')
async def get_asteroids(message: Message) -> None:
    """Обработчик команды получения информации об астероидах."""
    logger.info("Обработчик астероидов вызван")
    try:
        today = date.today().isoformat()
        params = {
            "api_key": NASA_API_KEY,
            "start_date": today,
            "end_date": today
        }
        
        data = await neo_client.get("neo/rest/v1/feed", params=params)
        logger.debug(f"Получены данные об астероидах: {data}")
        
        asteroids = data.get('near_earth_objects', {}).get(today, [])
        
        if not asteroids:
            await message.answer("На сегодня нет данных об астероидах. Попробуйте позже.")
            return
        
        # Сортируем по близости подлета к Земле
        asteroids.sort(
            key=lambda x: float(x['close_approach_data'][0]['miss_distance']['kilometers'])
        )
        
        logger.debug(f"Отсортированные астероиды: {asteroids[:5]}")
        
        # Отправляем информацию последовательно, чтобы избежать ошибок с порядком сообщений
        for ast in asteroids[:5]:
            try:
                await send_asteroid_info(message, ast)
                await asyncio.sleep(0.5)  # Небольшая задержка между сообщениями
            except Exception as e:
                logger.error(f"Ошибка при отправке информации об астероиде {ast.get('name', 'Unknown')}: {e}")
        
    except Exception as e:
        logger.error(f"Ошибка при получении данных об астероидах: {e}")
        await message.answer(
            "Извините, произошла ошибка при получении данных об астероидах. "
            "Попробуйте позже."
        )

async def send_asteroid_info(message: Message, ast: Dict[str, Any]) -> None:
    """Отправляет информацию об одном астероиде."""
    try:
        logger.info(f"Отправка информации об астероиде: {ast['name']}")
        avg_size = (
            ast['estimated_diameter']['meters']['estimated_diameter_min'] +
            ast['estimated_diameter']['meters']['estimated_diameter_max']
        ) / 2
        
        text = (
            f"☄️ Астероид: {ast['name']}\n\n"
            f"📏 Размер: {ast['estimated_diameter']['meters']['estimated_diameter_min']:.1f}"
            f"-{ast['estimated_diameter']['meters']['estimated_diameter_max']:.1f} м\n"
            f"⚠️ Опасен: {'Да ☢️' if ast['is_potentially_hazardous_asteroid'] else 'Нет ✅'}\n"
            f"🔺 Макс. сближение: {float(ast['close_approach_data'][0]['miss_distance']['kilometers']):.0f} км\n"
            f"🚀 Скорость: {float(ast['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']):.0f} км/ч\n"
            f"⏰ Время сближения: {ast['close_approach_data'][0]['close_approach_date_full']}"
        )
        
        logger.info(f"Текст сообщения: {text}")
        
        # Отправляем только текстовое сообщение, без изображения
        await message.answer(
            text,
            parse_mode="HTML"
        )
        logger.info("Сообщение успешно отправлено")

    except Exception as e:
        logger.error(f"Ошибка при отправке информации об астероиде: {e}")
        await message.answer(
            f"Информация об астероиде {ast['name']}:\n{text}"
        )

@router.message(F.text.startswith("🔴 Марс"))
@track_performance()
@cache_response(cache_type='mars_photos')
async def get_mars_photos(message: Message) -> None:
    """Обработчик команды получения фотографий с Марса с выбором камеры и пагинацией."""
    logger.info("Обработчик Марса вызван")
    try:
        rovers: List[str] = ["curiosity", "perseverance"]
        rover: str = random.choice(rovers)
        logger.debug(f"Выбран ровер: {rover}")

        # Предлагаем пользователю выбрать камеру через кнопки
        cameras = {
            "FHAZ": "Front Hazard Avoidance Camera",
            "RHAZ": "Rear Hazard Avoidance Camera",
            "MAST": "Mast Camera",
            "CHEMCAM": "Chemistry and Camera Complex",
            "NAVCAM": "Navigation Camera"
        }

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=value, callback_data=f"mars_camera:{key}:{rover}")]
            for key, value in cameras.items()
        ])

        await message.answer(
            "Выберите камеру для фотографий с Марса:",
            reply_markup=keyboard
        )

    except TelegramForbiddenError:
        logger.warning("Пользователь заблокировал бота. Сообщение не может быть отправлено.")
    except Exception as e:
        logger.error(f"Ошибка при подготовке выбора камеры: {e}")
        await message.answer(
            "Извините, произошла ошибка при подготовке выбора камеры. "
            "Попробуйте позже."
        )

@router.callback_query(F.data.startswith("mars_camera"))
async def handle_camera_selection(callback: CallbackQuery) -> None:
    """Обработчик выбора камеры для фотографий с Марса."""
    try:
        _, selected_camera, rover = callback.data.split(":")
        logger.debug(f"Пользователь выбрал камеру: {selected_camera} для ровера: {rover}")

        params = {
            "api_key": NASA_API_KEY,
            "sol": "1000",
            "camera": selected_camera,  # Выбор камеры
            "page": 1  # Пагинация
        }

        url = f"/mars-photos/api/v1/rovers/{rover}/photos"
        logger.debug(f"Запрос к API: {url} с параметрами {params}")
        data = await nasa_client.get(url, params=params)
        logger.info(f"Ответ API: {data}")

        if photos := data.get('photos', []):
            for photo in photos[:5]:  # Отправляем первые 5 фотографий
                image_data = await nasa_client.get_bytes(photo['img_src'])
                optimized_image = await optimize_image(image_data)

                caption = (
                    f"📸 Фото с марсохода {photo['rover']['name']}\n"
                    f"📅 Дата съёмки: {photo['earth_date']}\n"
                    f"🎥 Камера: {photo['camera']['full_name']}"
                )

                try:
                    await callback.message.answer_photo(
                        photo=BufferedInputFile(optimized_image, "mars.jpg"),
                        caption=caption
                    )
                except TelegramForbiddenError:
                    logger.warning("Пользователь заблокировал бота. Сообщение не может быть отправлено.")
        else:
            await callback.message.answer("К сожалению, фотографии не найдены. Попробуйте позже.")
            logger.info("Фотографии не найдены в ответе API")

    except TelegramForbiddenError:
        logger.warning("Пользователь заблокировал бота. Сообщение не может быть отправлено.")
    except Exception as e:
        logger.error(f"Ошибка при получении фото с Марса: {e}")
        await callback.message.answer(
            "Извините, произошла ошибка при получении фотографий. "
            "Попробуйте позже."
        )

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
        "✨ Экзопланеты - Каталог известных экзопланет\n\n"
        "👨‍💼 Административные команды:\n"
        "/stats - Статистика производительности\n"
        "/cache_clear - Очистка кэша"
    )

@router.message(F.text == "🌍 Земля")
async def get_earth_image(message: Message) -> None:
    """Обработчик команды получения спутниковых снимков Земли."""
    await message.answer(
        "Для получения спутникового снимка, отправьте мне координаты в формате:\n"
        "latitude,longitude\n\n"
        "Например: 55.7558,37.6173 (Москва)",
        reply_markup=keyboards.get_back_keyboard()
    )

@router.message(F.text.regexp(r'^-?\d+\.?\d*,-?\d+\.?\d*$'))
@cache_response(cache_type='earth_imagery')
async def process_coordinates(message: Message) -> None:
    """Обработчик получения координат для спутникового снимка."""
    try:
        lat, lon = map(float, message.text.split(','))
        
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            await message.answer(
                "Некорректные координаты! Широта должна быть от -90 до 90, "
                "долгота от -180 до 180."
            )
            return
        
        params = {
            "api_key": NASA_API_KEY,
            "lat": lat,
            "lon": lon,
            "dim": 0.3,
            "date": date.today().isoformat()
        }
        
        image_data = await earth_client.get_bytes("/earth/imagery", params=params)
        optimized_image = await optimize_image(image_data)
        
        caption = f"🌍 Спутниковый снимок локации: {lat}, {lon}"
        
        await message.answer_photo(
            photo=BufferedInputFile(optimized_image, "earth.jpg"),
            caption=caption,
            reply_markup=keyboards.get_back_keyboard()
        )
            
    except ValueError:
        await message.answer(
            "Неверный формат координат. Пожалуйста, используйте формат: latitude,longitude\n"
            "Например: 55.7558,37.6173"
        )
    except Exception as e:
        logger.error(f"Ошибка при получении снимка Земли: {e}")
        await message.answer(
            "Извините, произошла ошибка при получении снимка. "
            "Попробуйте позже."
        )

@router.callback_query(F.data == "main_menu")
async def return_to_main_menu(callback: CallbackQuery) -> None:
    """Обработчик команды возврата в главное меню."""
    await callback.message.answer(
        "Выберите интересующий вас раздел:",
        reply_markup=keyboards.main_keyboard
    )
    await callback.answer()
