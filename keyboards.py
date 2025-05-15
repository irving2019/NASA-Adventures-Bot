from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# Основная клавиатура
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="🌠 APOD"), KeyboardButton(text="☄️ Астероиды")],
    [KeyboardButton(text="🔴 Марс"), KeyboardButton(text="🌍 Земля")],
    [KeyboardButton(text="🌞 Солнечная система"), KeyboardButton(text="✨ Экзопланеты")],
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

# Клавиатура для планет Солнечной системы
planets_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="☀️ Солнце", callback_data="planet_sun")],
    [InlineKeyboardButton(text="🌍 Меркурий", callback_data="planet_mercury"),
     InlineKeyboardButton(text="🌍 Венера", callback_data="planet_venus")],
    [InlineKeyboardButton(text="🌍 Земля", callback_data="planet_earth"),
     InlineKeyboardButton(text="🔴 Марс", callback_data="planet_mars")],
    [InlineKeyboardButton(text="🌟 Юпитер", callback_data="planet_jupiter"),
     InlineKeyboardButton(text="💫 Сатурн", callback_data="planet_saturn")],
    [InlineKeyboardButton(text="⭐ Уран", callback_data="planet_uranus"),
     InlineKeyboardButton(text="✨ Нептун", callback_data="planet_neptune")]
])

# Клавиатура для экзопланет (отсортирована по индексу землеподобия - ESI)
exoplanets_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1️⃣ Teegarden b", callback_data="exo_teegardenb"),
     InlineKeyboardButton(text="2️⃣ Kepler-442b", callback_data="exo_kepler442b")],
    [InlineKeyboardButton(text="3️⃣ TRAPPIST-1e", callback_data="exo_trappist1_e"),
     InlineKeyboardButton(text="4️⃣ Kepler-186f", callback_data="exo_kepler186f")],
    [InlineKeyboardButton(text="5️⃣ Proxima Centauri b", callback_data="exo_proxima_b"),
     InlineKeyboardButton(text="6️⃣ Kepler-452b", callback_data="exo_kepler452b")],
    [InlineKeyboardButton(text="7️⃣ Kepler-62f", callback_data="exo_kepler62f"),
     InlineKeyboardButton(text="8️⃣ TOI-700d", callback_data="exo_toi700d")],
    [InlineKeyboardButton(text="9️⃣ LHS 1140b", callback_data="exo_lhs1140b"),
     InlineKeyboardButton(text="🔟 K2-18b", callback_data="exo_k218b")],
    [InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")]
])