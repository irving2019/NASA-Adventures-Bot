from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def start(message: Message):
    await message.reply(f"Привет!\nТвой ID: {message.from_user.id}\nИмя: {message.from_user.first_name}"
                        f"\nЖми /help чтобы ознакомиться с командами бота!")

@router.message(Command("help"))
async def help(message: Message):
    await message.answer('''Список команд и фраз для взаимодействия с ботом:
    /help - справка
    Как дела?
    /get_photo - получить фото
    ''')

@router.message(F.text == "Как дела?")
async def how_are_you(message: Message):
    await message.answer("Всё хорошо!")

@router.message(Command("get_photo"))
async def get_photo(message: Message):
    await message.answer_photo(photo="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBR6Voh2SVNpOvGa374VfvspEiwKRtbMLUcA&s",
                               caption="Улыбнись!")


@router.message(F.photo)
async def photo(message: Message):
    await message.answer(f'ID фото: {message.photo[-1].file_id}')