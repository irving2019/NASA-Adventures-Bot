import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_TOKEN
import nasa_handlers
import planet_handlers
import iss_handlers
import space_events_handlers
import quiz_handlers
import admin_handlers


# Настройка логирования
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрация роутеров с обработчиками
dp.include_router(nasa_handlers.router)
dp.include_router(planet_handlers.router)
dp.include_router(iss_handlers.router)
dp.include_router(space_events_handlers.router)
dp.include_router(quiz_handlers.router)
dp.include_router(admin_handlers.router)  # Административные команды

async def main() -> None:
    """
    Основная асинхронная функция для запуска бота.
    
    Выполняет следующие действия:
    1. Удаляет старый webhook если он был установлен
    2. Запускает поллинг обновлений
    3. Обрабатывает возможные ошибки при выполнении
    4. Гарантирует корректное закрытие сессии бота
    
    Returns:
        None
        
    Raises:
        Exception: Любые исключения, возникшие при работе бота
    """
    logger.info("Запуск бота...")
    
    # Удаление webhook на случай, если он был установлен
    await bot.delete_webhook(drop_pending_updates=True)
    
    try:
        # Логируем успешный запуск
        logger.info(f"Бот успешно запущен: {datetime.now()}")
        
        # Запускаем бота
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error(f"Произошла ошибка: {e}")
        
    finally:
        # Закрываем сессию бота
        await bot.session.close()
        logger.info("Бот остановлен")

if __name__ == '__main__':
    try:
        # Настройка базового логирования
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Запуск бота
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise