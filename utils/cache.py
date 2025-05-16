"""
Модуль для кэширования данных API запросов.

Использует оптимизированный in-memory кэш с временем жизни для хранения
результатов запросов к API NASA. Поддерживает мониторинг попаданий/промахов
и автоматическую очистку устаревших данных.
"""

import time
import logging
from typing import Any, Dict, Optional, Union, List, Tuple
from functools import wraps
from collections import OrderedDict
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from .cache_config import CACHE_SETTINGS, DEFAULT_CACHE_TTL, DEFAULT_CACHE_SIZE


logger = logging.getLogger(__name__)


class TTLCache:
    """
    Оптимизированный in-memory кэш с TTL и мониторингом.
    
    Attributes:
        ttl (int): Время жизни элементов в секундах
        maxsize (int): Максимальный размер кэша
        cache (OrderedDict): Хранилище кэшированных данных
        timestamps (Dict): Хранилище временных меток
        metrics (Dict): Метрики использования кэша
        _cleanup_lock (threading.Lock): Блокировка для очистки кэша
        _executor (ThreadPoolExecutor): Пул потоков для фоновых задач
    """
    
    def __init__(self, ttl: int = DEFAULT_CACHE_TTL, maxsize: int = DEFAULT_CACHE_SIZE):
        self.ttl = ttl
        self.maxsize = maxsize
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[str, float] = {}
        self.metrics = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'size': 0
        }
        self._cleanup_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._schedule_cleanup()
        
    def _schedule_cleanup(self) -> None:
        """Планирует периодическую очистку кэша."""
        self._executor.submit(self._cleanup_expired)
        
    def _cleanup_expired(self) -> None:
        """Очищает устаревшие элементы из кэша."""
        try:
            with self._cleanup_lock:
                current_time = time.time()
                expired_keys = [
                    key for key, timestamp in self.timestamps.items()
                    if current_time - timestamp > self.ttl
                ]
                
                for key in expired_keys:
                    self._remove_item(key)
                    self.metrics['evictions'] += 1
                
                self.metrics['size'] = len(self.cache)
                
                # Логируем статистику кэша
                if expired_keys:
                    logger.info(
                        f"Cache cleanup: removed {len(expired_keys)} items. "
                        f"Current size: {self.metrics['size']}"
                    )
        except Exception as e:
            logger.error(f"Error during cache cleanup: {e}")
        finally:
            # Планируем следующую очистку через TTL/2
            threading.Timer(self.ttl / 2, self._cleanup_expired).start()
            
    def _remove_item(self, key: str) -> None:
        """Удаляет элемент из кэша."""
        self.cache.pop(key, None)
        self.timestamps.pop(key, None)
        
    def get(self, key: str) -> Optional[Any]:
        """
        Получает значение из кэша если оно не устарело.
        
        Args:
            key (str): Ключ кэша
            
        Returns:
            Optional[Any]: Значение из кэша или None
        """
        try:
            if key not in self.cache:
                self.metrics['misses'] += 1
                return None
                
            if time.time() - self.timestamps[key] > self.ttl:
                self._remove_item(key)
                self.metrics['evictions'] += 1
                self.metrics['misses'] += 1
                return None
                
            self.metrics['hits'] += 1
            
            # Обновляем позицию элемента (LRU)
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
            
        except Exception as e:
            logger.error(f"Error getting item from cache: {e}")
            return None
        
    def set(self, key: str, value: Any) -> None:
        """
        Сохраняет значение в кэш.
        
        Args:
            key (str): Ключ кэша
            value (Any): Значение для сохранения
        """
        try:
            with self._cleanup_lock:
                if len(self.cache) >= self.maxsize:
                    # Удаляем самый старый элемент (LRU)
                    oldest = next(iter(self.cache))
                    self._remove_item(oldest)
                    self.metrics['evictions'] += 1
                    
                self.cache[key] = value
                self.timestamps[key] = time.time()
                self.metrics['size'] = len(self.cache)
                
        except Exception as e:
            logger.error(f"Error setting item in cache: {e}")
            
    def clear(self) -> None:
        """Очищает кэш."""
        with self._cleanup_lock:
            self.cache.clear()
            self.timestamps.clear()
            self.metrics['size'] = 0
            self.metrics['evictions'] += len(self.cache)
            
    def get_metrics(self) -> Dict[str, int]:
        """
        Возвращает метрики использования кэша.
        
        Returns:
            Dict[str, int]: Словарь с метриками
        """
        hit_ratio = self.metrics['hits'] / (self.metrics['hits'] + self.metrics['misses']) * 100 if self.metrics['hits'] + self.metrics['misses'] > 0 else 0
        return {
            **self.metrics,
            'hit_ratio': f"{hit_ratio:.1f}%"
        }


# Создаем кэши для разных типов данных
caches = {}

def get_cache_for_type(cache_type: str) -> TTLCache:
    """
    Получает или создает кэш для определенного типа данных.
    
    Args:
        cache_type (str): Тип кэша из cache_config.CACHE_SETTINGS
        
    Returns:
        TTLCache: Экземпляр кэша для указанного типа
    """
    if cache_type not in caches:
        settings = CACHE_SETTINGS.get(cache_type, {
            'ttl': DEFAULT_CACHE_TTL,
            'max_size': DEFAULT_CACHE_SIZE
        })
        caches[cache_type] = TTLCache(
            ttl=settings['ttl'],
            maxsize=settings['max_size']
        )
    return caches[cache_type]

def cache_response(cache_type: str = None):
    """
    Декоратор для кэширования ответов API с мониторингом.
    
    Args:
        cache_type (str): Тип кэша из cache_config.CACHE_SETTINGS
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from utils.monitoring import monitor
            
            # Определяем тип кэша или используем имя функции
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache = get_cache_for_type(cache_type or func.__name__)
            
            # Проверяем кэш
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                monitor.record_cache_hit(cache_type or func.__name__)
                return cached_result
            
            # Кэш-мисс
            monitor.record_cache_miss(cache_type or func.__name__)
            
            # Получаем новые данные
            result = await func(*args, **kwargs)
            
            # Кэшируем результат
            cache.set(cache_key, result)
            
            return result
        return wrapper
    return decorator
