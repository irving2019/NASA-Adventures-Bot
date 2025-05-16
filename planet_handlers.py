"""
Модуль обработчиков команд для работы с информацией о планетах.
"""

import logging
import aiohttp
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.types.input_file import BufferedInputFile

from data.planets import SOLAR_SYSTEM, EXOPLANETS
import keyboards
from utils.monitoring import track_performance
from utils.cache import cache_response

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.text == "🌞 Солнечная система")
async def show_planets(message: Message):
    await message.answer(
        "Выберите объект Солнечной системы для получения информации:",
        reply_markup=keyboards.get_planets_keyboard()
    )

@router.message(F.text == "✨ Экзопланеты")
@track_performance()
async def show_exoplanets(message: Message):
    """Показывает список доступных экзопланет."""
    try:
        await message.answer(
            "🌌 Выберите экзопланету для получения подробной информации:",
            reply_markup=keyboards.exoplanets_keyboard
        )
    except Exception as e:
        logger.error(f"Ошибка при отображении списка экзопланет: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

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
                await callback.message.answer_photo(
                    photo=planet['image'],
                    caption=info
                )
            except Exception as e:
                logger.error(f"Ошибка при отправке фото планеты {planet_id}: {str(e)}")
                await callback.message.answer(info)
        else:
            logger.error(f"Планета {planet_id} не найдена в базе данных")
            await callback.message.answer("Извините, информация о данном объекте временно недоступна")
    except Exception as e:
        logger.error(f"Ошибка при обработке информации о планете: {str(e)}")
        await callback.message.answer("Произошла ошибка при получении информации. Попробуйте позже.")
    
    await callback.answer()

@router.callback_query(F.data.startswith("exo_"))
@track_performance()
@cache_response(cache_type='exoplanet_info')
async def show_exoplanet_info(callback: CallbackQuery):
    """Показывает информацию о выбранной экзопланете."""
    try:
        await callback.answer()
        exo_id = callback.data.replace("exo_", "").lower()
        if exo_id in EXOPLANETS:
            planet = EXOPLANETS[exo_id]
            description = (f"{planet['name']}\n\n"
                f"🌍 Тип: {planet['type']}\n"
                f"📏 Масса: {planet['mass']}\n"
                f"🌟 Звезда: {planet['star']}\n"
                f"📅 Год: {planet['year']}\n"
                f"📍 Расстояние: {planet['distance']}\n"
                f"🌫️ Атмосфера: {planet['atmosphere']}\n"
                f"🌐 Индекс схожести с Землей (ESI): {planet['esi']}\n\n"
                f"📝 {planet['description']}")

            try:
                # Загружаем изображение напрямую через aiohttp
                async with aiohttp.ClientSession() as session:
                    async with session.get(planet['image']) as response:
                        if response.status == 200:
                            image_data = await response.read()
                            await callback.message.answer_photo(
                                photo=BufferedInputFile(image_data, f"{exo_id}.jpg"),
                                caption=description,
                                reply_markup=keyboards.get_back_keyboard()
                            )
                        else:
                            logger.error(f"Ошибка при загрузке изображения {planet['image']}: {response.status}")
                            await callback.message.answer(
                                text=f"{description}\n\n⚠️ Изображение временно недоступно",
                                reply_markup=keyboards.get_back_keyboard()
                            )
            except Exception as img_error:
                logger.error(f"Ошибка при загрузке изображения экзопланеты: {img_error}")
                await callback.message.answer(
                    text=f"{description}\n\n⚠️ Изображение временно недоступно",
                    reply_markup=keyboards.get_back_keyboard()
                )
        else:
            await callback.message.answer("❌ Информация об этой экзопланете недоступна.")
            
    except Exception as e:
        logger.error(f"Ошибка при отображении информации об экзопланете: {e}")
        await callback.message.answer("❌ Произошла ошибка. Попробуйте позже.")
