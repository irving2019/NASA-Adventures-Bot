import logging
import random

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import keyboards


logger = logging.getLogger(__name__)
router = Router()


class QuizState(StatesGroup):
    waiting_for_answer = State()

# База вопросов для викторины
QUIZ_QUESTIONS = {
    "easy": [
        {
            "question": "Какая планета находится ближе всего к Солнцу?",
            "options": ["Венера", "Меркурий", "Марс", "Земля"],
            "correct": 1
        },
        {
            "question": "Как называется галактика, в которой находится наша Солнечная система?",
            "options": ["Андромеда", "Млечный Путь", "Треугольник", "Сомбреро"],
            "correct": 1
        },
        {
            "question": "Какая планета известна своими кольцами?",
            "options": ["Юпитер", "Уран", "Сатурн", "Нептун"],
            "correct": 2
        }
    ],
    "medium": [
        {
            "question": "Какой спутник является крупнейшим в Солнечной системе?",
            "options": ["Титан", "Европа", "Ганимед", "Фобос"],
            "correct": 2
        },
        {
            "question": "Какое созвездие также известно как 'Большой Ковш'?",
            "options": ["Кассиопея", "Большая Медведица", "Орион", "Лебедь"],
            "correct": 1
        },
        {
            "question": "Сколько времени требуется свету, чтобы достичь Земли от Солнца?",
            "options": ["4 минуты", "8 минут", "16 минут", "32 минуты"],
            "correct": 1
        }
    ],
    "hard": [
        {
            "question": "Какой объект считается первой обнаруженной экзопланетой?",
            "options": ["51 Пегаса b", "Kepler-186f", "HD 209458 b", "TRAPPIST-1e"],
            "correct": 0
        },
        {
            "question": "Какой тип звезды станет наше Солнце в конце своей жизни?",
            "options": ["Красный гигант", "Белый карлик", "Нейтронная звезда", "Черная дыра"],
            "correct": 1
        },
        {
            "question": "Какое явление описывает гравитационное искривление света?",
            "options": ["Красное смещение", "Линзирование", "Аберрация", "Параллакс"],
            "correct": 1
        }
    ]
}

@router.message(F.text == "❓ Викторина")
async def start_quiz(message: Message):
    await message.answer(
        "Добро пожаловать в космическую викторину! 🚀\n"
        "Выберите уровень сложности:",
        reply_markup=keyboards.quiz_keyboard
    )

@router.callback_query(F.data.startswith("quiz_"))
async def handle_quiz_difficulty(callback: CallbackQuery, state: FSMContext):
    difficulty = callback.data.split("_")[1]
    
    # Выбираем случайный вопрос из соответствующего уровня сложности
    question = random.choice(QUIZ_QUESTIONS[difficulty])
    
    # Сохраняем информацию о текущем вопросе
    await state.update_data(
        current_question=question,
        difficulty=difficulty,
        score=0
    )
    
    # Создаем клавиатуру с вариантами ответов
    options_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=option, callback_data=f"answer_{i}")]
            for i, option in enumerate(question["options"])
        ] + [[InlineKeyboardButton(text="« Главное меню", callback_data="main_menu")]]
    )
    
    await callback.message.answer(
        f"Вопрос:\n\n{question['question']}",
        reply_markup=options_keyboard
    )
    
    await state.set_state(QuizState.waiting_for_answer)
    await callback.answer()

@router.callback_query(F.data.startswith("answer_"), QuizState.waiting_for_answer)
async def handle_answer(callback: CallbackQuery, state: FSMContext):
    user_answer = int(callback.data.split("_")[1])
    data = await state.get_data()
    question = data["current_question"]
    
    if user_answer == question["correct"]:
        score = data.get("score", 0) + 1
        await callback.message.answer(
            "✅ Правильно!\n\n"
            "Хотите продолжить викторину?",
            reply_markup=keyboards.quiz_keyboard
        )
    else:
        correct_answer = question["options"][question["correct"]]
        await callback.message.answer(
            f"❌ Неправильно. Правильный ответ: {correct_answer}\n\n"
            "Хотите попробовать еще раз?",
            reply_markup=keyboards.quiz_keyboard
        )
    
    await state.clear()
    await callback.answer()
