from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from random import choice
from forms.user import (
    Form,
    group_1,
    group_2,
    group_3,
    group_4,
    group_5,
    group_6,
    bored,
    sad,
    tired,
    energetic,
    anxious,
    angry,
    lonely,
    happy,
)
import json
from pathlib import Path


router = Router()

# СОХРОНЯЕМ ВОЗРАСТ
USERS_FILE = Path(__file__).resolve().parents[1] / "users.json"


def load_users():
    if not USERS_FILE.exists():
        return {}

    return json.loads(
        USERS_FILE.read_text(encoding="utf-8")
    )


def save_user_age(user_id, age):
    users = load_users()
    users[str(user_id)] = {"age": age}

    USERS_FILE.write_text(
        json.dumps(users, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_user_age(user_id):
    users = load_users()
    user = users.get(str(user_id))

    if user is None:
        return None

    return user.get("age")

# ФУНКЦИЯ ДЛЯ ВЫБОРА РАНДОМНЫХ ЗАНЯТИЙ
def get_random_activity(mood, activities, age_group):
    rules = ACTIVITY_AGE_RULES

    suitable_activities = {
        number: activity
        for number, activity in activities.items()
        if (
            (mood, number) not in rules
            or age_group in rules[(mood, number)]
        )
    }

    return choice(list(suitable_activities.values()))


# Правила доступа к отдельным заданиям.
# Ключ: (название настроения, номер задания).
# Значение: возрастные группы, которым задание доступно.

ACTIVITY_AGE_RULES = {
    ("bored", 14): (group_3, group_4, group_5, group_6),
    ("bored", 18): (group_3, group_4, group_5, group_6),
}


# ОПРЕДЕЛЯЕМ ВОЗРАСТ В ГРУППЫ
def get_age_group(age):
    if group_1[0] <= age <= group_1[1]:
        return group_1
    elif group_2[0] <= age <= group_2[1]:
        return group_2
    elif group_3[0] <= age <= group_3[1]:
        return group_3
    elif group_4[0] <= age <= group_4[1]:
        return group_4
    elif group_5[0] <= age <= group_5[1]:
        return group_5
    elif group_6[0] <= age <= group_6[1]:
        return group_6

    return None


def get_main_reply_keyboard():
    """Клавиатура с кнопкой Старт."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Старт")],
        ],
        resize_keyboard=True,
    )


def get_main_reply_keyboard_mood():
    """Клавиатура для выбора настроения с коротким текстом."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Скучно 🥱")],
            [KeyboardButton(text="Грустно 😢")],
            [KeyboardButton(text="Устал(а) 😮‍💨")],
            [KeyboardButton(text="Много энергии ⚡")],
            [KeyboardButton(text="Тревожно 😰")],
            [KeyboardButton(text="Злюсь 😡")],
            [KeyboardButton(text="Одиноко 🫂")],
            [KeyboardButton(text="Всё отлично! ✨")],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

# СОЗДАЕМ КНОПКИ ВНУТРИ ДИАЛОГА
def get_activity_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить возраст",
                    callback_data="change_age",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить настроение",
                    callback_data="change_mood",
                )
            ],
        ]
    )


# СОЗДАЕМ КОМАНДУ СТАРТ
@router.message(Command("start"))
@router.message(F.text.casefold() == "старт")
async def start(message: Message, state: FSMContext):
    age = get_user_age(message.from_user.id)

    if age is None:
        await state.set_state(Form.age)

        await message.answer(
            "Привет! 😊 Сколько тебе лет?",
            reply_markup=get_main_reply_keyboard(),
        )
    else:
        await state.update_data(age=age)
        await state.set_state(Form.mood)

        await message.answer(
            f"С возвращением! Я помню, тебе {age} лет 😊\n"
            "Какое у тебя сейчас настроение?",
            reply_markup=get_main_reply_keyboard_mood(),
        )


# СОЗДАЕМ КОМАНДУ ПО ВОЗРАСТУ
@router.message(Form.age, F.text)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть целым числом.")
        return

    age = int(message.text)

    if not 5 <= age <= 100:
        await message.answer("Возраст должен быть от 5 до 100 лет.")
        return

    age_group = get_age_group(age)

    save_user_age(message.from_user.id, age)

    await state.update_data(
        age=age,
        age_group=age_group,
    )
    await state.set_state(Form.mood)

    await message.answer(
        "Отлично! Какое у тебя сейчас настроение?",
        reply_markup=get_main_reply_keyboard_mood(),
    )


# ФУНКЦИЯ ПО ВЫБОРУ НАСТРОЕНИЯ
def get_activities_by_mood(mood):
    activities_by_mood = {
        "Скучно 🥱": bored,
        "Грустно 😢": sad,
        "Устал(а) 😮‍💨": tired,
        "Много энергии ⚡": energetic,
        "Тревожно 😰": anxious,
        "Злюсь 😡": angry,
        "Одиноко 🫂": lonely,
        "Всё отлично! ✨": happy,
    }
    return activities_by_mood.get(mood)

# СОЗДАЕМ КОМАНДУ ВЫБОРА НАСТРОЕНИЯ
@router.message(Form.mood, F.text)
async def process_mood(message: Message, state: FSMContext):
    activities = get_activities_by_mood(message.text)

    if activities is None:
        await message.answer(
            "Пожалуйста, выбери настроение с клавиатуры."
        )
        return

    age = get_user_age(message.from_user.id)
    age_group = get_age_group(age)

    mood_names = {
        "Скучно 🥱": "bored",
        "Грустно 😢": "sad",
        "Устал(а) 😮‍💨": "tired",
        "Много энергии ⚡": "energetic",
        "Тревожно 😰": "anxious",
        "Злюсь 😡": "angry",
        "Одиноко 🫂": "lonely",
        "Всё отлично! ✨": "happy",
    }

    mood = mood_names[message.text]

    activity = get_random_activity(
        mood,
        activities,
        age_group,
    )

    await message.answer(
        f"Вот идея для тебя:\n\n{activity}",
        reply_markup=get_activity_keyboard(),
    )

    await state.set_state(None)


# СОЗДАЕМ КОМАНДУ КНОПКИ В ДИАЛОГЕ ПО СМЕНЕ ВОЗРАСТА
@router.callback_query(F.data == "change_age")
async def change_age(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_reply_markup(
        reply_markup=None
    )
    await state.set_state(Form.age)

    await callback.message.answer(
        "Хорошо! Введи свой новый возраст 😊",
        reply_markup=get_main_reply_keyboard(),
    )

    await callback.answer()


# СОЗДАЕМ КОМАНДУ КНОПКИ В ДИАЛОГЕ ПО СМЕНЕ НАСТРОЕНИЯ
@router.callback_query(F.data == "change_mood")
async def change_mood(
    callback: CallbackQuery,
    state: FSMContext,
):
    await callback.message.edit_reply_markup(
        reply_markup=None
    )
    await state.set_state(Form.mood)

    await callback.message.answer(
        "Какое у тебя сейчас настроение?",
        reply_markup=get_main_reply_keyboard_mood(),
    )

    await callback.answer()


















