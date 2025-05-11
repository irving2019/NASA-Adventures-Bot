from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[

    [KeyboardButton(text="Каталог")],
    [KeyboardButton(text="Корзина"), KeyboardButton(text="Контакты")]
     #Расклад по рядам
], resize_keyboard=True, # оптимизация кнопок
   input_field_placeholder="Выберите пункт меню") # Сообщение в наборе


settings = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Telegram", url="https://t.me/voldemarnif")]])