# Основной файл запуска телеграм-бота
import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from config import TOKEN
from handlers import router

# Настройка логирования
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
from aiogram.client.default import DefaultBotProperties

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Регистрация роутера с обработчиками
dp.include_router(router)

async def main():
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