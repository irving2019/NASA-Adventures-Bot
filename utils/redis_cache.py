"""
Модуль для кэширования с использованием Redis.

Предоставляет интерфейс для кэширования данных в Redis
с поддержкой сериализации/десериализации и TTL.
"""

import json
import pickle
from typing import Any, Optional, Union
import aioredis
import os

from config import REDIS_URL

class RedisCache:
    """
    Класс для работы с Redis кэшем.
    
    Attributes:
        redis (aioredis.Redis): Клиент Redis
        default_ttl (int): Время жизни кэша по умолчанию в секундах
    """
    
    def __init__(self, url: str = None, default_ttl: int = 3600):
        """
        Инициализация Redis кэша.
        
        Args:
            url (str): URL подключения к Redis
            default_ttl (int): Время жизни кэша по умолчанию
        """
        self.redis = aioredis.from_url(
            url or os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        )
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Получение значения из кэша.
        
        Args:
            key (str): Ключ кэша
            
        Returns:
            Any: Значение из кэша или None, если значение не найдено
        """
        try:
            data = await self.redis.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            print(f"Ошибка при получении из Redis: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Сохранение значения в кэш.
        
        Args:
            key (str): Ключ кэша
            value (Any): Значение для сохранения
            ttl (int, optional): Время жизни в секундах
            
        Returns:
            bool: True если значение успешно сохранено
        """
        try:
            data = pickle.dumps(value)
            await self.redis.set(
                key,
                data,
                ex=ttl or self.default_ttl
            )
            return True
        except Exception as e:
            print(f"Ошибка при сохранении в Redis: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удаление значения из кэша."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            print(f"Ошибка при удалении из Redis: {e}")
            return False
    
    async def clear(self) -> bool:
        """Очистка всего кэша."""
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            print(f"Ошибка при очистке Redis: {e}")
            return False

# Глобальный экземпляр кэша
redis_cache = RedisCache()
