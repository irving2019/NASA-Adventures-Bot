"""
Модуль для мониторинга производительности бота.

Собирает и анализирует метрики производительности,
включая статистику кэширования и времени ответа API.
"""

import logging
import time
from typing import Dict, Any, Optional
from functools import wraps
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """
    Монитор производительности для сбора и анализа метрик.
    
    Attributes:
        _metrics (Dict): Хранилище метрик
        _api_timings (Dict): Статистика времени ответа API
        _cache_stats (Dict): Статистика использования кэша
    """
    
    def __init__(self):
        self._metrics = defaultdict(int)
        self._api_timings = defaultdict(list)
        self._cache_stats = defaultdict(lambda: {'hits': 0, 'misses': 0})
        self._last_reset = datetime.now()
    
    def record_api_call(self, endpoint: str, duration: float) -> None:
        """Записывает время выполнения API запроса."""
        self._api_timings[endpoint].append(duration)
        self._metrics['total_api_calls'] += 1
    
    def record_cache_hit(self, cache_type: str) -> None:
        """Записывает попадание в кэш."""
        self._cache_stats[cache_type]['hits'] += 1
        
    def record_cache_miss(self, cache_type: str) -> None:
        """Записывает промах кэша."""
        self._cache_stats[cache_type]['misses'] += 1
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Возвращает статистику API запросов."""
        stats = {}
        for endpoint, timings in self._api_timings.items():
            if timings:
                avg_time = sum(timings) / len(timings)
                max_time = max(timings)
                min_time = min(timings)
                stats[endpoint] = {
                    'avg_time': f"{avg_time:.2f}s",
                    'max_time': f"{max_time:.2f}s",
                    'min_time': f"{min_time:.2f}s",
                    'calls': len(timings)
                }
        return stats
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Возвращает статистику использования кэша."""
        stats = {}
        for cache_type, data in self._cache_stats.items():
            total = data['hits'] + data['misses']
            if total > 0:
                hit_ratio = (data['hits'] / total) * 100
                stats[cache_type] = {
                    'hit_ratio': f"{hit_ratio:.1f}%",
                    'hits': data['hits'],
                    'misses': data['misses']
                }
        return stats
    
    def get_summary(self) -> Dict[str, Any]:
        """Возвращает сводную статистику."""
        uptime = datetime.now() - self._last_reset
        return {
            'uptime': str(uptime).split('.')[0],
            'total_api_calls': self._metrics['total_api_calls'],
            'api_stats': self.get_api_stats(),
            'cache_stats': self.get_cache_stats()
        }
    
    def reset(self) -> None:
        """Сбрасывает все метрики."""
        self._metrics.clear()
        self._api_timings.clear()
        self._cache_stats.clear()
        self._last_reset = datetime.now()


# Глобальный экземпляр монитора
monitor = PerformanceMonitor()


def track_performance():
    """
    Декоратор для отслеживания производительности функций.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                monitor.record_api_call(func.__name__, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                monitor.record_api_call(f"{func.__name__}_error", duration)
                raise
        return wrapper
    return decorator
