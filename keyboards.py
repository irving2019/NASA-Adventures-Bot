from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

#main = ReplyKeyboardMarkup(keyboard=[
    #[KeyboardButton(text="Каталог")],
    #[KeyboardButton(text="Корзина"),
    # KeyboardButton(text="Контакты")]
#], resize_keyboard=True, input_field_placeholder="Выберите пункт меню.")

main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Каталог", callback_data="catalog")],
    [InlineKeyboardButton(text="Корзина", callback_data="basket"), InlineKeyboardButton(text="Контакты", callback_data="contacts")],
])

settings = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Telegram", url="https://t.me/voldemarnif")]])

cars = ["Tesla", "Mercedes", "BMW", "Porsche"]


async def inline_cars():
    keyboard = InlineKeyboardBuilder()
    for car in cars:
        keyboard.add(InlineKeyboardButton(text=car, callback_data=f'car_{car}'))
    return keyboard.adjust(2).as_markup() # По 2 кнопки на 1 ряд
