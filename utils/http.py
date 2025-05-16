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
                if not self.session:
                    conn = aiohttp.TCPConnector(
                        limit=100,
                        enable_cleanup_closed=True,
                        force_close=True
                    )
                    timeout = aiohttp.ClientTimeout(
                        total=60,      # Общий таймаут
                        connect=10,    # Таймаут на подключение
                        sock_read=30   # Таймаут на чтение
                    )
                    self.session = aiohttp.ClientSession(
                        connector=conn,
                        headers=self.headers,
                        timeout=timeout
                    )
    
    async def close(self) -> None:
        """Закрытие клиента."""
        if self.session:
            await self.session.close()
            self.session = None
    
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[aiohttp.ClientSession, None]:
        """Получение сессии с автоматической инициализацией."""
        if not self.session:
            await self.init()
        assert self.session is not None
        try:
            yield self.session
        except Exception:
            await self.close()
            raise
    
    async def get(self, url: str, **kwargs) -> Any:
        """GET-запрос к API с повторными попытками."""
        if not url.startswith('http'):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        else:
            full_url = url
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                async with self.get_session() as session:
                    async with session.get(full_url, **kwargs) as response:
                        response.raise_for_status()
                        return await response.json()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay * (attempt + 1))
                await self.close()  # Пересоздаем сессию после ошибки
    
    async def get_bytes(self, url: str, **kwargs) -> bytes:
        """GET-запрос с получением бинарных данных и повторными попытками."""
        if not url.startswith('http'):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        else:
            full_url = url
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                async with self.get_session() as session:
                    async with session.get(full_url, **kwargs) as response:
                        response.raise_for_status()
                        return await response.read()
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(retry_delay * (attempt + 1))
                await self.close()  # Пересоздаем сессию после ошибки


# Создаем глобальные клиенты для разных API
nasa_client = APIClient("https://api.nasa.gov")
neo_client = APIClient("https://api.nasa.gov")
earth_client = APIClient("https://api.nasa.gov")
iss_client = APIClient(
    "http://api.open-notify.org",
    headers={"User-Agent": "SpaceBot/1.0 (Educational Project)"}
)
