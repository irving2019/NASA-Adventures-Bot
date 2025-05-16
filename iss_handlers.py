import logging
from datetime import datetime
import asyncio

import aiohttp
import pytz
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.types.input_file import BufferedInputFile

from config import (
    ISS_LOCATION_URL, ISS_CREW_URL, ISS_PASS_URL, NASA_API_KEY
)
import keyboards

logger = logging.getLogger(__name__)
router = Router()

# Словарь для хранения состояний пользователей
user_states = {}

@router.message(F.text == "🛸 МКС")
async def show_iss_options(message: Message):
    await message.answer(
        "Выберите, что вы хотите узнать о МКС:",
        reply_markup=keyboards.iss_keyboard
    )

@router.callback_query(F.data == "iss_location")
async def get_iss_location(callback: CallbackQuery):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(ISS_LOCATION_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    lat = float(data['iss_position']['latitude'])
                    lon = float(data['iss_position']['longitude'])
                    timestamp = datetime.fromtimestamp(data['timestamp'], tz=pytz.UTC)
                    
                    # Формируем ссылку на карту
                    map_url = f"https://www.google.com/maps?q={lat},{lon}&z=3"
                    
                    await callback.message.answer(
                        f"🛸 Текущее положение МКС:\n\n"
                        f"📍 Широта: {lat}°\n"
                        f"📍 Долгота: {lon}°\n"
                        f"🕒 Время: {timestamp.strftime('%H:%M:%S')} UTC\n\n"
                        f"🗺 [Посмотреть на карте]({map_url})",
                        parse_mode="Markdown"
                    )
                else:
                    await callback.message.answer("Извините, не удалось получить данные о положении МКС.")
        except Exception as e:
            logger.error(f"Ошибка при получении положения МКС: {str(e)}")
            await callback.message.answer("Произошла ошибка при получении данных. Попробуйте позже.")
    
    await callback.answer()

@router.callback_query(F.data == "iss_crew")
async def get_iss_crew(callback: CallbackQuery):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(ISS_CREW_URL) as response:
                if response.status == 200:
                    data = await response.json()
                    crew = [person for person in data['people'] if person['craft'] == 'ISS']
                    
                    message = "👨‍🚀 Текущий экипаж МКС:\n\n"
                    for i, person in enumerate(crew, 1):
                        message += f"{i}. {person['name']}\n"
                    
                    message += f"\nВсего на борту: {len(crew)} человек"
                    await callback.message.answer(message)
                else:
                    await callback.message.answer("Извините, не удалось получить данные об экипаже МКС.")
        except Exception as e:
            logger.error(f"Ошибка при получении данных об экипаже МКС: {str(e)}")
            await callback.message.answer("Произошла ошибка при получении данных. Попробуйте позже.")
    
    await callback.answer()

@router.callback_query(F.data == "iss_stream")
async def get_iss_stream(callback: CallbackQuery):
    await callback.message.answer(
        "🎥 Прямая трансляция с МКС:\n\n"
        "HD камера: https://ustream.tv/channel/iss-hdev-payload\n"
        "Стандартный поток: https://ustream.tv/channel/live-iss-stream\n\n"
        "Примечание: трансляция может быть недоступна, когда МКС находится в тени Земли "
        "или при потере сигнала."
    )
    await callback.answer()

@router.callback_query(F.data == "iss_pass")
async def request_location_for_pass(callback: CallbackQuery):
    await callback.message.answer(
        "Чтобы узнать, когда МКС пролетит над вашим местоположением, "
        "отправьте координаты в формате: lat, lon\n"
        "Например: 55.75, 37.62 (Москва)"
    )
    await callback.answer()

@router.callback_query(F.data == "iss_passes")
async def request_city_name(callback: CallbackQuery):
    """Запрашивает название города для получения пролётов МКС."""
    user_states[callback.from_user.id] = "waiting_for_city"
    await callback.message.answer(
        "Чтобы узнать время пролётов МКС над вашим городом:\n\n"
        "1. Отправьте название вашего города\n"
        "2. Или отправьте координаты в формате: широта, долгота\n\n"
        "Пример: Москва\n"
        "Или: 55.75, 37.62"
    )
    await callback.answer()

@router.callback_query(F.data == "iss_photos")
async def show_iss_photos(callback: CallbackQuery):
    """Показывает последние фотографии с МКС."""
    try:
        await callback.message.answer("🔍 Ищу последние фотографии с МКС...")
        
        # Используем NASA Images API
        async with aiohttp.ClientSession() as session:
            nasa_api_url = "https://images-api.nasa.gov/search"
            params = {
                'q': 'ISS astronaut earth',
                'media_type': 'image',
                'year_start': '2023',
                'keywords': 'ISS,International Space Station,Earth'
            }
            
            async with session.get(nasa_api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if items := data.get('collection', {}).get('items', []):
                        # Фильтруем результаты, чтобы получить только фото с МКС
                        iss_photos = [
                            item for item in items 
                            if any(keyword in item.get('data', [{}])[0].get('title', '').lower() 
                                  for keyword in ['iss', 'space station', 'astronaut'])
                        ][:5]
                        
                        if iss_photos:
                            for item in iss_photos:
                                try:
                                    # Получаем оригинальное изображение
                                    image_url = item['links'][0]['href']
                                    metadata = item['data'][0]
                                    title = metadata.get('title', 'Без названия')
                                    date = metadata.get('date_created', 'Дата неизвестна')
                                    description = metadata.get('description', 'Описание отсутствует')
                                    
                                    # Загружаем и отправляем фото
                                    async with session.get(image_url) as img_response:
                                        if img_response.status == 200:
                                            img_data = await img_response.read()
                                            caption = (
                                                f"📷 {title}\n"
                                                f"📅 {date[:10]}\n\n"
                                                f"{description[:200]}..."
                                            )
                                            await callback.message.answer_photo(
                                                photo=BufferedInputFile(img_data, f"iss_photo.jpg"),
                                                caption=caption
                                            )
                                            await asyncio.sleep(0.5)  # Задержка между фото
                                except Exception as img_error:
                                    logger.error(f"Ошибка при обработке фото: {img_error}")
                                    continue
                        else:
                            await callback.message.answer("😔 Не удалось найти актуальные фотографии с МКС.")
                    else:
                        await callback.message.answer("😔 Фотографии не найдены.")
        
        async with aiohttp.ClientSession() as session:
            params = {
                'q': 'ISS Earth photography',
                'media_type': 'image',
                'year_start': '2023',
                'api_key': NASA_API_KEY
            }
            
            url = "https://images-api.nasa.gov/search"
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    items = data.get('collection', {}).get('items', [])
                    
                    if items:
                        await callback.message.answer("📸 Вот несколько последних фотографий с МКС:")
                        sent_count = 0
                        
                        for item in items[:5]:  # Берём первые 5 фото
                            try:
                                if 'links' in item and item['links']:
                                    image_url = item['links'][0]['href']
                                    data = item['data'][0]
                                    title = data.get('title', 'Без названия')
                                    date = data.get('date_created', 'Дата неизвестна')
                                    description = data.get('description', 'Описание отсутствует')
                                    
                                    # Ограничиваем длину описания
                                    if len(description) > 200:
                                        description = description[:200] + "..."
                                    
                                    caption = (
                                        f"📷 {title}\n"
                                        f"📅 Дата: {date[:10]}\n\n"
                                        f"📝 {description}"
                                    )
                                    
                                    # Получаем изображение напрямую
                                    async with session.get(image_url) as img_response:
                                        if img_response.status == 200:
                                            img_data = await img_response.read()
                                            await callback.message.answer_photo(
                                                photo=BufferedInputFile(
                                                    img_data,
                                                    filename=f"iss_photo_{sent_count}.jpg"
                                                ),
                                                caption=caption
                                            )
                                            sent_count += 1
                                            await asyncio.sleep(0.5)  # Задержка между фото
                            except Exception as e:
                                logger.error(f"Ошибка при отправке фото: {e}")
                                continue
                        
                        if sent_count == 0:
                            await callback.message.answer(
                                "😔 К сожалению, не удалось загрузить фотографии. "
                                "Попробуйте посмотреть прямую трансляцию с МКС."
                            )
                    else:
                        await callback.message.answer(
                            "😔 Фотографии не найдены. Попробуйте посмотреть "
                            "прямую трансляцию с МКС."
                        )
                else:
                    await callback.message.answer(
                        "❌ Ошибка при получении фотографий. Попробуйте позже."
                    )
    except Exception as e:
        logger.error(f"Ошибка при получении фотографий с МКС: {str(e)}")
        await callback.message.answer(
            "❌ Произошла ошибка при получении фотографий. "
            "Попробуйте позже или посмотрите прямую трансляцию с МКС."
        )
    
    await callback.answer()

@router.message(lambda message: message.text and ',' in message.text and 
                message.reply_to_message and 
                "МКС пролетит" in message.reply_to_message.text)
async def get_iss_pass_predictions(message: Message):
    try:
        lat, lon = map(float, message.text.split(','))
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Координаты вне допустимого диапазона")
        
        async with aiohttp.ClientSession() as session:
            params = {
                "lat": lat,
                "lon": lon,
                "n": 5  # Количество пролетов
            }
            
            async with session.get(ISS_PASS_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data['response']:
                        message_text = f"🛸 Ближайшие пролеты МКС над точкой {lat}, {lon}:\n\n"
                        
                        for pass_time in data['response']:
                            duration = pass_time['duration']  # в секундах
                            timestamp = datetime.fromtimestamp(pass_time['risetime'], tz=pytz.UTC)
                            local_time = timestamp.astimezone()
                            
                            message_text += (
                                f"📅 {local_time.strftime('%d.%m.%Y')}\n"
                                f"🕒 {local_time.strftime('%H:%M:%S')} (местное время)\n"
                                f"⏱ Продолжительность: {duration // 60} мин {duration % 60} сек\n\n"
                            )
                        
                        await message.answer(message_text)
                    else:
                        await message.answer(
                            "К сожалению, в ближайшее время МКС не пролетит над указанной точкой."
                        )
                else:
                    await message.answer(
                        "Извините, не удалось получить данные о пролетах МКС."
                    )
    except ValueError:
        await message.answer(
            "Пожалуйста, введите координаты в правильном формате: latitude, longitude\n"
            "Например: 55.75, 37.62"
        )
    except Exception as e:
        logger.error(f"Ошибка при получении данных о пролетах МКС: {str(e)}")
        await message.answer("Произошла ошибка при получении данных. Попробуйте позже.")

async def get_city_coordinates(city_name: str) -> tuple[float, float] | None:
    """Получает координаты города через Nominatim API."""
    async with aiohttp.ClientSession() as session:
        try:
            url = f"https://nominatim.openstreetmap.org/search"
            params = {
                'q': city_name,
                'format': 'json',
                'limit': 1
            }
            headers = {'User-Agent': 'SpaceBot/1.0'}
            
            async with session.get(url, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        return float(data[0]['lat']), float(data[0]['lon'])
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении координат города {city_name}: {e}")
            return None

async def get_iss_pass_times(lat: float, lon: float) -> str:
    """Получает прогноз пролётов МКС над указанной точкой."""
    async with aiohttp.ClientSession() as session:
        try:
            params = {
                'lat': lat,
                'lon': lon,
                'n': 5  # количество пролётов
            }
            async with session.get(ISS_PASS_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'response' in data:
                        passes = []
                        for pass_time in data['response']:
                            duration = int(pass_time['duration'])
                            time = datetime.fromtimestamp(pass_time['risetime'], tz=pytz.UTC)
                            local_time = time.astimezone()
                            
                            passes.append(
                                f"🛸 {local_time.strftime('%d.%m.%Y %H:%M:%S')}\n"
                                f"⏱ Продолжительность: {duration // 60} мин {duration % 60} сек"
                            )
                        
                        return "Ближайшие пролёты МКС:\n\n" + "\n\n".join(passes)
                return "Не удалось получить данные о пролётах МКС."
        except Exception as e:
            logger.error(f"Ошибка при получении данных о пролётах МКС: {e}")
            return f"Произошла ошибка при получении данных: {str(e)}"

@router.message(F.text)
async def process_city_input(message: Message):
    """Обрабатывает введённое название города или координаты."""
    # Проверяем, ожидаем ли мы ввод города от этого пользователя
    if user_states.get(message.from_user.id) != "waiting_for_city":
        return
        
    try:
        text = message.text.strip()
        
        # Проверяем, являются ли входные данные координатами
        if ',' in text:
            try:
                lat, lon = map(float, map(str.strip, text.split(',')))
                await message.answer(f"📍 Получаю данные для координат: {lat}, {lon}...")
                passes = await get_iss_pass_times(lat, lon)
                await message.answer(passes)
                return
            except ValueError:
                pass  # Если не удалось распарсить координаты, пробуем как название города
        
        # Обрабатываем как название города
        await message.answer(f"🔍 Ищу координаты города {text}...")
        coordinates = await get_city_coordinates(text)
        
        if coordinates:
            lat, lon = coordinates
            await message.answer(f"📍 Координаты найдены: {lat}, {lon}\nПолучаю данные о пролётах МКС...")
            passes = await get_iss_pass_times(lat, lon)
            await message.answer(passes)
        else:
            await message.answer(
                "❌ Не удалось найти координаты указанного города.\n"
                "Проверьте название или отправьте координаты вручную в формате: широта, долгота"
            )
    except Exception as e:
        logger.error(f"Ошибка при обработке города/координат: {e}")
        await message.answer("Произошла ошибка при обработке запроса. Попробуйте позже.")
    finally:
        # Очищаем состояние пользователя
        user_states.pop(message.from_user.id, None)
