from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# Основная клавиатура
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🌠 APOD"), KeyboardButton(text="☄️ Астероиды")],
    [KeyboardButton(text="🔴 Марс"), KeyboardButton(text="🌍 Земля")],
    [KeyboardButton(text="ℹ️ Помощь")]
], resize_keyboard=True, input_field_placeholder="Выберите опцию")

# Клавиатура для выбора марсохода
mars_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Curiosity", callback_data="mars_curiosity")],
    [InlineKeyboardButton(text="Perseverance", callback_data="mars_perseverance")],
    [InlineKeyboardButton(text="Opportunity", callback_data="mars_opportunity")]
])

# Клавиатура для навигации по датам
date_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ Предыдущий", callback_data="prev_date"),
     InlineKeyboardButton(text="Следующий ➡️", callback_data="next_date")],
    [InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")]
])