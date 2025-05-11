from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[

    [KeyboardButton(text="Каталог")],
    [KeyboardButton(text="Корзина"), KeyboardButton(text="Контакты")]
     #Расклад по рядам
], resize_keyboard=True, # оптимизация кнопок
   input_field_placeholder="Выберите пункт меню") # Сообщение в наборе


settings = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Telegram", url="https://t.me/voldemarnif")]])

cars = ["Tesla", "Mercedes", "BMW", "Porsche"]


async def inline_cars():
    keyboard = InlineKeyboardBuilder()
    for car in cars:
        keyboard.add(InlineKeyboardButton(text=car, url=f"https://t.me/voldemarnif"))
    return keyboard.adjust(2).as_markup() # По 2 кнопки на 1 ряд
