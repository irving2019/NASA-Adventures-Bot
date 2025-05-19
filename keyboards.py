"""
Модуль, содержащий все клавиатуры для бота.

Этот модуль определяет все интерактивные клавиатуры, используемые в боте,
включая основную клавиатуру и специализированные инлайн-клавиатуры для
различных функций (марсоходы, планеты, викторина).

Клавиатуры:
    main_keyboard: Основная клавиатура с главным меню
    mars_keyboard: Клавиатура для выбора марсохода
    quiz_keyboard: Клавиатура для выбора сложности викторины
    exoplanets_keyboard: Клавиатура для выбора экзопланеты
"""

from typing import List

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


# Основная клавиатура
main_keyboard: ReplyKeyboardMarkup = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="☄️ Астероиды"), KeyboardButton(text="🌞 Солнечная система")],
        [KeyboardButton(text="🌍 Земля"), KeyboardButton(text="🔴 Марс")],
        [KeyboardButton(text="✨ Экзопланеты"), KeyboardButton(text="❓ Викторина")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите опцию"
)

# Клавиатура для выбора марсохода
mars_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Curiosity", callback_data="mars_curiosity"),
        InlineKeyboardButton(text="Perseverance", callback_data="mars_perseverance")
    ],
    [InlineKeyboardButton(text="Opportunity", callback_data="mars_opportunity")],
    [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
])

# Клавиатура для викторины
quiz_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="Легкий", callback_data="quiz_easy"),
        InlineKeyboardButton(text="Средний", callback_data="quiz_medium"),
        InlineKeyboardButton(text="Сложный", callback_data="quiz_hard")
    ],
    [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
])

# Клавиатура для экзопланет
exoplanets_keyboard: InlineKeyboardMarkup = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="🌎 Kepler-452b", callback_data="exo_kepler_452b"),
        InlineKeyboardButton(text="🌍 Proxima b", callback_data="exo_proxima_b")
    ],
    [
        InlineKeyboardButton(text="🌎 TRAPPIST-1e", callback_data="exo_trappist_1e"),
        InlineKeyboardButton(text="🌍 K2-18b", callback_data="exo_k2_18b")
    ],
    [
        InlineKeyboardButton(text="🌎 Teegarden b", callback_data="exo_teegarden_b"),
        InlineKeyboardButton(text="🌍 LHS 1140b", callback_data="exo_lhs_1140b")
    ],
    [
        InlineKeyboardButton(text="🌎 GJ 257d", callback_data="exo_gj_257d"),
        InlineKeyboardButton(text="🌍 Ross 128b", callback_data="exo_ross_128b")
    ],
    [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
])


def get_planets_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для выбора планеты Солнечной системы.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками планет
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="☀️ Солнце", callback_data="planet_sun"),
            InlineKeyboardButton(text="☿️ Меркурий", callback_data="planet_mercury"),
            InlineKeyboardButton(text="♀️ Венера", callback_data="planet_venus")
        ],
        [
            InlineKeyboardButton(text="🌍 Земля", callback_data="planet_earth"),
            InlineKeyboardButton(text="♂️ Марс", callback_data="planet_mars")
        ],
        [
            InlineKeyboardButton(text="♃ Юпитер", callback_data="planet_jupiter"),
            InlineKeyboardButton(text="♄ Сатурн", callback_data="planet_saturn")
        ],
        [
            InlineKeyboardButton(text="⛢ Уран", callback_data="planet_uranus"),
            InlineKeyboardButton(text="♆ Нептун", callback_data="planet_neptune")
        ],
        [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
    ])


def get_quiz_answer_keyboard(options: List[str], correct_index: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с вариантами ответов для викторины.
    
    Args:
        options (List[str]): Список вариантов ответов
        correct_index (int): Индекс правильного ответа
        
    Returns:
        InlineKeyboardMarkup: Клавиатура с вариантами ответов
    """
    keyboard = []
    for i, option in enumerate(options):
        callback_data = f"quiz_answer_{i}_{1 if i == correct_index else 0}"
        keyboard.append([InlineKeyboardButton(text=option, callback_data=callback_data)])
    
    keyboard.append([InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_mars_photos_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для просмотра фотографий с Марса.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопками управления просмотром
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔄 Другое фото", callback_data="mars_next"),
            InlineKeyboardButton(text="🎥 Другая камера", callback_data="mars_camera")
        ],
        [InlineKeyboardButton(text="📅 Другой день", callback_data="mars_date")],
        [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
    ])


def get_back_keyboard() -> InlineKeyboardMarkup:
    """
    Создает простую клавиатуру с кнопкой возврата в главное меню.
    
    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой возврата
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]
    ])