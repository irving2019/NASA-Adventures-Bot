import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import keyboards
import aiohttp
from data.planets import SOLAR_SYSTEM, EXOPLANETS

# Настройка логирования
logger = logging.getLogger(__name__)

router = Router()

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
            
            try:
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
