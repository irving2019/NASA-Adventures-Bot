import logging
from datetime import datetime, timedelta

import aiohttp
import pytz
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from config import (
    LAUNCHES_URL,
    EVENTS_URL,
    SPACE_WEATHER_URL,
    NASA_API_KEY
)
import keyboards


logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "🚀 Запуски")
async def get_upcoming_launches(message: Message):
    async with aiohttp.ClientSession() as session:
        try:
            params = {
                "limit": 5,
                "offset": 0
            }
            async with session.get(LAUNCHES_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    launches = data.get('results', [])
                    
                    if not launches:
                        await message.answer("Нет данных о предстоящих запусках.")
                        return
                    
                    for launch in launches:
                        # Форматируем время запуска
                        launch_time = datetime.fromisoformat(launch['net'].replace('Z', '+00:00'))
                        local_time = launch_time.astimezone()
                        
                        text = (
                            f"🚀 {launch['name']}\n\n"
                            f"📅 Дата: {local_time.strftime('%d.%m.%Y')}\n"
                            f"🕒 Время: {local_time.strftime('%H:%M')} (местное)\n"
                            f"🏢 Компания: {launch['launch_service_provider']['name']}\n"
                            f"📍 Место: {launch['pad']['name']}\n"
                            f"🎯 Миссия: {launch['mission']['description'][:500] if launch['mission'] else 'Нет данных'}\n"
                        )
                        
                        # Пытаемся отправить изображение, если оно есть
                        if launch.get('image'):
                            try:
                                await message.answer_photo(
                                    photo=launch['image'],
                                    caption=text
                                )
                            except Exception:
                                await message.answer(text)
                        else:
                            await message.answer(text)
                else:
                    await message.answer("Извините, не удалось получить данные о запусках.")
        except Exception as e:
            logger.error(f"Ошибка при получении данных о запусках: {str(e)}")
            await message.answer("Произошла ошибка при получении данных. Попробуйте позже.")

@router.message(F.text == "📅 События")
async def show_events_menu(message: Message):
    await message.answer(
        "Выберите тип космических событий:",
        reply_markup=keyboards.events_keyboard
    )

@router.callback_query(F.data.startswith("events_"))
async def get_space_events(callback: CallbackQuery):
    event_type = callback.data.split("_")[1]
    
    async with aiohttp.ClientSession() as session:
        try:
            params = {
                "limit": 5,
                "offset": 0
            }
            
            if event_type == "launches":
                url = LAUNCHES_URL
            else:
                url = EVENTS_URL
                params["type"] = event_type
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    events = data.get('results', [])
                    
                    if not events:
                        await callback.message.answer("Нет данных о предстоящих событиях этого типа.")
                        return
                    
                    for event in events:
                        event_time = datetime.fromisoformat(event['date'].replace('Z', '+00:00'))
                        local_time = event_time.astimezone()
                        
                        text = (
                            f"📅 {event['name']}\n\n"
                            f"🕒 Дата: {local_time.strftime('%d.%m.%Y %H:%M')} (местное)\n"
                            f"📝 Описание: {event['description'][:500] if event['description'] else 'Нет описания'}\n"
                        )
                        
                        if event.get('image_url'):
                            try:
                                await callback.message.answer_photo(
                                    photo=event['image_url'],
                                    caption=text
                                )
                            except Exception:
                                await callback.message.answer(text)
                        else:
                            await callback.message.answer(text)
                else:
                    await callback.message.answer("Извините, не удалось получить данные о событиях.")
        except Exception as e:
            logger.error(f"Ошибка при получении данных о событиях: {str(e)}")
            await callback.message.answer("Произошла ошибка при получении данных. Попробуйте позже.")
    
    await callback.answer()

@router.message(F.text == "🌡️ Косм. погода")
async def get_space_weather(message: Message):
    async with aiohttp.ClientSession() as session:
        try:
            # Получаем данные за последние 3 дня
            start_date = (datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d")
            end_date = datetime.now().strftime("%Y-%m-%d")
            
            params = {
                "api_key": NASA_API_KEY,
                "startDate": start_date,
                "endDate": end_date
            }
            
            async with session.get(SPACE_WEATHER_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if not data:
                        await message.answer(
                            "За последние дни не было значительных космических погодных явлений."
                        )
                        return
                    
                    # Группируем уведомления по типам
                    events = {}
                    for notification in data:
                        event_type = notification['messageType']
                        if event_type not in events:
                            events[event_type] = []
                        events[event_type].append(notification)
                    
                    # Отправляем сводку по каждому типу событий
                    for event_type, notifications in events.items():
                        text = f"🌡️ {event_type}:\n\n"
                        for notif in notifications[:3]:  # Берем только 3 последних события каждого типа
                            message_time = datetime.fromisoformat(notif['messageIssueTime'].replace('Z', '+00:00'))
                            local_time = message_time.astimezone()
                            
                            text += (
                                f"⏰ {local_time.strftime('%d.%m.%Y %H:%M')}\n"
                                f"📝 {notif['messageBody'][:300]}...\n\n"
                            )
                        
                        await message.answer(text)
                else:
                    await message.answer("Извините, не удалось получить данные о космической погоде.")
        except Exception as e:
            logger.error(f"Ошибка при получении данных о космической погоде: {str(e)}")
            await message.answer("Произошла ошибка при получении данных. Попробуйте позже.")
