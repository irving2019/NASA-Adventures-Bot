"""
Модуль обработчиков команд для взаимодействия с API NASA.

Этот модуль содержит обработчики для различных команд, связанных с получением
данных от NASA API, включая:
- Информацию о околоземных астероидах
- Фотографии с марсоходов
- Спутниковые снимки Земли

Attributes:
    router (Router): Роутер для обработки команд, связанных с NASA API
    logger (Logger): Логгер для записи событий модуля
"""

import aiohttp
import asyncio
import logging
import random

from datetime import date, datetime, timedelta
from io import BytesIO
from PIL import Image
from typing import Dict, Optional, Any

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message, 
    CallbackQuery,
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    BufferedInputFile
)

from config import NASA_API_KEY
from data.rovers import ROVERS
from utils.cache import cache_response
from utils.http import nasa_client
from utils.monitoring import track_performance
import keyboards


logger = logging.getLogger(__name__)
router = Router()

# Константы
MAX_IMAGE_SIZE = (1280, 1280)  # Максимальный размер изображения
CACHE_TIME = 3600  # Время кэширования в секундах

async def optimize_image(image_data: bytes, max_size: tuple = (1280, 1280)) -> bytes:
    """Оптимизирует размер изображения для отправки в Telegram."""
    try:
        with BytesIO(image_data) as img_file:
            img = Image.open(img_file)
            
            # Конвертируем в RGB если нужно
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Уменьшаем размер если нужно
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Сохраняем оптимизированное изображение
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            return output.getvalue()
    except Exception as e:
        logger.error(f"Ошибка при оптимизации изображения: {e}")
        return image_data

@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start."""
    await message.answer(
        "Привет! Я космический бот NASA. Я могу показать вам:\n"
        "☄️ Информацию о приближающихся астероидах\n"
        "🌞 Информацию о планетах Солнечной системы\n"
        "🌍 Спутниковые снимки Земли\n"
        "🔴 Фотографии с Марса\n"
        "✨ Каталог экзопланет\n"
        "❓ Космическую викторину\n\n"
        "Используйте клавиатуру ниже для навигации:",
        reply_markup=keyboards.main_keyboard
    )

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
        
        data = await nasa_client.get("/neo/rest/v1/feed", params=params)
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

@router.message(F.text == "🔴 Марс")
@track_performance()
@cache_response(cache_type='mars_photos')
async def get_mars_photos(message: Message) -> None:
    """Обработчик команды получения фотографий с Марса."""
    logger.info("Обработчик Марса вызван")
    try:
        # Создаем клавиатуру для выбора марсохода
        buttons = []
        for rover_id, rover_info in ROVERS.items():
            if rover_id in ['curiosity', 'perseverance']:  # Только активные марсоходы
                buttons.append([InlineKeyboardButton(
                    text=f"🤖 {rover_info['name']}",
                    callback_data=f"get_rover_photo:{rover_id}"
                )])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        
        await message.answer(
            "🔴 *Марсианские исследования*\n\n"
            "Выберите марсоход для просмотра последних фотографий:",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )

    except Exception as e:
        logger.error(f"Ошибка при подготовке выбора марсохода: {e}")
        await message.answer("Извините, произошла ошибка. Попробуйте позже.")

@router.callback_query(F.data.startswith("get_rover_photo"))
async def get_rover_photo(callback: CallbackQuery) -> None:
    """Обработчик получения случайной фотографии с марсохода."""
    try:
        await callback.answer()
        _, rover = callback.data.split(":")
        
        # Пробуем получить последние фото
        url = f"mars-photos/api/v1/rovers/{rover}/latest_photos"
        data = await nasa_client.get(url, params={"api_key": NASA_API_KEY})
        
        if not data.get('latest_photos'):
            await callback.message.answer(
                f"К сожалению, для марсохода {ROVERS[rover]['name']} "
                f"не удалось получить последние фотографии. Попробуйте позже."
            )
            return

        # Выбираем случайное фото из последних
        photo = random.choice(data['latest_photos'])
        image_data = await nasa_client.get_bytes(photo['img_src'])
        optimized_image = await optimize_image(image_data)

        caption = (
            f"📸 Фото с марсохода {photo['rover']['name']}\n"
            f"📅 Дата съёмки: {photo['earth_date']}\n"
            f"🎥 Камера: {photo['camera']['full_name']}\n"
            f"📍 Сол: {photo.get('sol', 'N/A')}"
        )

        # Добавляем кнопку для получения нового фото
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Ещё фото",
                    callback_data=f"get_rover_photo:{rover}"
                )
            ]
        ])

        await callback.message.answer_photo(
            photo=BufferedInputFile(optimized_image, "mars.jpg"),
            caption=caption,
            reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Ошибка при получении фото с Марса: {e}")
        await callback.message.answer(
            "Извините, произошла ошибка при получении фотографий. "
            "Попробуйте позже."
        )



@router.message(F.text == "ℹ️ Помощь")
async def show_help(message: Message) -> None:
    await message.answer(
        "🚀 Команды бота:\n\n"
        "/start - Начать работу с ботом\n"
        "☄️ Астероиды - Информация о околоземных астероидах\n"
        "🌞 Солнечная система - Информация о планетах\n"
        "🌍 Земля - Спутниковые снимки Земли\n"
        "🔴 Марс - Фотографии с марсоходов\n"
        "✨ Экзопланеты - Каталог экзопланет\n"
        "❓ Викторина - Космическая викторина\n\n"
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
        # Показываем сообщение о загрузке
        loading_message = await message.answer("🔄 Получаю спутниковый снимок...")
        
        lat, lon = map(float, message.text.split(','))
        
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            await loading_message.edit_text(
                "⚠️ Некорректные координаты! Широта должна быть от -90 до 90, "
                "долгота от -180 до 180."
            )
            return
        
        # Пробуем получить более новый снимок сначала
        today = date.today()
        dates_to_try = [
            today - timedelta(days=x) for x in [0, 30, 60, 90, 180]
        ]
        
        image_data = None
        used_date = None
        
        for try_date in dates_to_try:
            try:
                params = {
                    "api_key": NASA_API_KEY,
                    "lat": lat,
                    "lon": lon,
                    "dim": 0.3,
                    "date": try_date.isoformat()
                }
                
                image_data = await nasa_client.get_bytes("/planetary/earth/imagery", params=params)
                if image_data:
                    used_date = try_date
                    break
            except Exception as e:
                logger.warning(f"Не удалось получить снимок за {try_date}: {e}")
                continue
        
        if not image_data:
            await loading_message.edit_text(
                "❌ К сожалению, не удалось найти спутниковые снимки для этих координат. "
                "Попробуйте другие координаты или повторите запрос позже."
            )
            return
            
        # Оптимизируем изображение
        optimized_image = await optimize_image(image_data)
        
        # Удаляем сообщение о загрузке
        await loading_message.delete()
        
        # Формируем подпись
        caption = (
            f"🌍 Спутниковый снимок локации:\n"
            f"📍 Широта: {lat:.4f}°\n"
            f"📍 Долгота: {lon:.4f}°\n"
            f"📅 Дата снимка: {used_date.strftime('%d.%m.%Y')}"
        )
        
        # Отправляем фото
        await message.answer_photo(
            photo=BufferedInputFile(optimized_image, "earth.jpg"),
            caption=caption,
            reply_markup=keyboards.get_back_keyboard()
        )
            
    except ValueError:
        await message.answer(
            "⚠️ Неверный формат координат. Пожалуйста, используйте формат: широта,долгота\n"
            "Например: 55.7558, 37.6173 (Москва)"
        )
    except Exception as e:
        logger.error(f"Ошибка при получении снимка Земли: {e}")
        await message.answer(
            "❌ Извините, произошла ошибка при получении снимка. "
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
