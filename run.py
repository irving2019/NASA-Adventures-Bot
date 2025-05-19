"""Main bot module."""
import admin_handlers
import asyncio
import logging
import nasa_handlers
import planet_handlers
import quiz_handlers
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN, LOG_LEVEL, LOG_FORMAT, LOG_FILE

logger = logging.getLogger(__name__)

def setup_logging():
    """Configure logging settings."""
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    formatter = logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
      # Настраиваем обработчик для консоли с явным указанием кодировки
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    
    # Настраиваем обработчик для файла с явным указанием кодировки UTF-8
    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8', mode='a')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    
    # Отключаем логи от библиотек ниже уровня WARNING
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('aiogram').setLevel(logging.WARNING)

# Инициализация бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрация роутеров с обработчиками
dp.include_router(nasa_handlers.router)
dp.include_router(planet_handlers.router)
dp.include_router(quiz_handlers.router)
dp.include_router(admin_handlers.router)  # Административные команды

async def main() -> None:
    """Start and run the bot."""
    logger.info("Starting bot...")
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Bot %s started successfully", (await bot.get_me()).username)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except Exception as e:
        logger.error("Critical bot error: %s", e, exc_info=True)
        raise
        
    finally:
        await bot.session.close()
        logger.info("Bot stopped")

if __name__ == '__main__':
    try:
        # Настраиваем расширенное логирование
        setup_logging()
        logger.info("Инициализация бота...")
        
        # Запуск бота
        asyncio.run(main())
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        raise