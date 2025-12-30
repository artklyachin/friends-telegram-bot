"""
Клавиатуры для бота
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Создать тест")],
            [KeyboardButton(text="Пройти тест")],
            [KeyboardButton(text="Мой тест")],
            [KeyboardButton(text="Информация")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_height_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора роста"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="140-159")],
            [KeyboardButton(text="160-179")],
            [KeyboardButton(text="180-199")],
            [KeyboardButton(text="200+")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_eye_color_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора цвета глаз"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Карие")],
            [KeyboardButton(text="Голубые")],
            [KeyboardButton(text="Зелёные")],
            [KeyboardButton(text="Серые")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_fear_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора страха"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Высоты")],
            [KeyboardButton(text="Темноты")],
            [KeyboardButton(text="Пауков")],
            [KeyboardButton(text="Одиночества")]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_create_test_button() -> InlineKeyboardMarkup:
    """Кнопка для создания своего теста после прохождения"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Создать свой тест дружбы", callback_data="create_test_after")]
        ]
    )
    return keyboard

