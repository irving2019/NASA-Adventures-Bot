# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Установка зависимостей системы
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка переменных окружения Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Создаем нового пользователя
RUN useradd -m -u 1000 bot_user && \
    chown -R bot_user:bot_user /app

# Переключаемся на непривилегированного пользователя
USER bot_user

# Копируем остальные файлы проекта
COPY --chown=bot_user:bot_user . .

# Запускаем бота
CMD ["python", "run.py"]
