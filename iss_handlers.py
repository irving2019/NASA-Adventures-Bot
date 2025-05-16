import logging
from datetime import datetime

import aiohttp
import pytz
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import ISS_LOCATION_URL, ISS_CREW_URL, ISS_PASS_URL
import keyboards


logger = logging.getLogger(__name__)
router = Router()

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
