"""
Модуль, содержащий все клавиатуры для бота
"""
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


# Основная клавиатура
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
    [KeyboardButton(text="🌠 APOD"), KeyboardButton(text="☄️ Астероиды")],
    [KeyboardButton(text="🔴 Марс"), KeyboardButton(text="🌍 Земля")],
    [KeyboardButton(text="🌞 Солнечная система"), KeyboardButton(text="✨ Экзопланеты")],
    [KeyboardButton(text="🛸 МКС"), KeyboardButton(text="🚀 Запуски")],
    [KeyboardButton(text="📅 События"), KeyboardButton(text="🌡️ Косм. погода")],
    [KeyboardButton(text="❓ Викторина"), KeyboardButton(text="ℹ️ Помощь")]
], resize_keyboard=True, input_field_placeholder="Выберите опцию")

# Клавиатура для выбора марсохода
mars_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Curiosity", callback_data="mars_curiosity"),
     InlineKeyboardButton(text="Perseverance", callback_data="mars_perseverance")],
    [InlineKeyboardButton(text="Opportunity", callback_data="mars_opportunity")],
    [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
])

# Клавиатура для календаря событий
events_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Запуски", callback_data="events_launches"),
     InlineKeyboardButton(text="Затмения", callback_data="events_eclipses")],
    [InlineKeyboardButton(text="Метеорные потоки", callback_data="events_meteors"),
     InlineKeyboardButton(text="Другие события", callback_data="events_other")],
    [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
])

# Клавиатура для викторины
quiz_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Легкий", callback_data="quiz_easy"),
     InlineKeyboardButton(text="Средний", callback_data="quiz_medium"),
     InlineKeyboardButton(text="Сложный", callback_data="quiz_hard")],
    [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
])

# Клавиатура для МКС
iss_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📍 Где сейчас МКС?", callback_data="iss_location"),
     InlineKeyboardButton(text="👨‍🚀 Экипаж", callback_data="iss_crew")],
    [InlineKeyboardButton(text="🎥 Трансляция", callback_data="iss_stream"),
     InlineKeyboardButton(text="⏰ Пролёты", callback_data="iss_pass")],
    [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
])

# Клавиатура для возврата в главное меню
date_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
])