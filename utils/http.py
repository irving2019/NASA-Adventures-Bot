"""
Модуль для управления HTTP-сессиями и клиентами.

Предоставляет оптимизированные клиенты для работы с API
с поддержкой повторного использования соединений и пула сессий.
"""

import aiohttp
from typing import Optional, Dict, Any, AsyncGenerator
import asyncio
from contextlib import asynccontextmanager


class APIClient:
    """
    Клиент для работы с API с поддержкой пула соединений.
    
    Attributes:
        session (aiohttp.ClientSession): Сессия для HTTP-запросов
        base_url (str): Базовый URL API
        headers (Dict): Заголовки по умолчанию
    """
    
    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.headers = headers or {}
        self.session: Optional[aiohttp.ClientSession] = None
        self._lock = asyncio.Lock()
        
    async def init(self) -> None:
        """Инициализация клиента."""
        if not self.session:
            async with self._lock:
                if not self.session:  # Двойная проверка для избежания race condition
                    # Увеличиваем количество одновременных соединений
                    conn = aiohttp.TCPConnector(limit=100)
                    self.session = aiohttp.ClientSession(
                        connector=conn,
                        headers=self.headers,
                        raise_for_status=True,
                        timeout=aiohttp.ClientTimeout(total=30)
                    )
    
    async def close(self) -> None:
        """Закрытие клиента."""
        if self.session:
            await self.session.close()
            self.session = None
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator['aiohttp.ClientSession', None]:
        """Получение сессии с автоматической инициализацией."""
        if not self.session:
            await self.init()
        assert self.session is not None
        try:
            yield self.session
        except Exception:
            # В случае критической ошибки пересоздаем сессию
            await self.close()
            raise
    
    async def get(self, url: str, **kwargs) -> Any:
        """GET-запрос к API."""
        if not url.startswith('http'):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        else:
            full_url = url
        
        async with self.get_session() as session:
            async with session.get(full_url, **kwargs) as response:
                return await response.json()
    
    async def get_bytes(self, url: str, **kwargs) -> bytes:
        """GET-запрос с получением бинарных данных."""
        if not url.startswith('http'):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        else:
            full_url = url
            
        async with self.get_session() as session:
            async with session.get(full_url, **kwargs) as response:
                return await response.read()


# Создаем глобальные клиенты для разных API
nasa_client = APIClient("https://api.nasa.gov")
neo_client = APIClient("https://api.nasa.gov")  # Используем общий базовый URL
earth_client = APIClient("https://api.nasa.gov")  # Используем общий базовый URL
iss_client = APIClient("http://api.open-notify.org")
