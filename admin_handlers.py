"""
Модуль для административных команд бота.

Содержит команды для мониторинга производительности,
управления кэшем и просмотра статистики.
"""

import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

from utils.cache import caches
from utils.monitoring import monitor

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("stats"))
async def show_stats(message: Message) -> None:
    """
    Показывает статистику производительности бота.
    
    Args:
        message (Message): Входящее сообщение
    """
    try:
        # Получаем статистику
        stats = monitor.get_summary()
        
        # Формируем сообщение
        text = "📊 Статистика бота\n\n"
        
        # Общая информация
        text += f"⏱ Время работы: {stats['uptime']}\n"
        text += f"📡 Всего API запросов: {stats['total_api_calls']}\n\n"
        
        # Статистика API
        text += "🔄 Статистика API:\n"
        for endpoint, data in stats['api_stats'].items():
            text += f"- {endpoint}:\n"
            text += f"  • Среднее время: {data['avg_time']}\n"
            text += f"  • Макс. время: {data['max_time']}\n"
            text += f"  • Мин. время: {data['min_time']}\n"
            text += f"  • Запросов: {data['calls']}\n"
        
        text += "\n📦 Статистика кэша:\n"
        for cache_type, data in stats['cache_stats'].items():
            text += f"- {cache_type}:\n"
            text += f"  • Hit ratio: {data['hit_ratio']}\n"
            text += f"  • Hits: {data['hits']}\n"
            text += f"  • Misses: {data['misses']}\n"
        
        await message.answer(text)
        
    except Exception as e:
        logger.error(f"Error showing stats: {e}")
        await message.answer("Ошибка при получении статистики.")


@router.message(Command("cache_clear"))
async def clear_cache(message: Message) -> None:
    """
    Очищает все кэши бота.
    
    Args:
        message (Message): Входящее сообщение
    """
    try:
        # Очищаем все кэши
        for cache_type, cache in caches.items():
            cache.clear()
        
        await message.answer("✅ Все кэши очищены.")
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        await message.answer("Ошибка при очистке кэша.")
