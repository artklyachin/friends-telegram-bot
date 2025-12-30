"""
Обработчики для создания теста
"""
import uuid
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from states import CreateTestStates
from keyboards import (
    get_main_menu_keyboard, get_height_keyboard, 
    get_eye_color_keyboard, get_fear_keyboard
)
from database import Database
import config

router = Router()
db = Database()


@router.message(F.text == "Создать тест")
async def start_test_creation(message: Message, state: FSMContext):
    """Начало создания теста"""
    await state.set_state(CreateTestStates.waiting_for_name)
    await message.answer(
        "Отлично! Давай создадим твой тест дружбы.\n\n"
        "📝 <b>Вопрос 1 из 4:</b>\n"
        "Как тебя зовут? (введи своё имя)",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove()  # убираем главное меню на время создания теста
    )


@router.message(CreateTestStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработка имени"""
    name = message.text.strip()
    if not name or len(name) > 100:
        await message.answer("Пожалуйста, введи корректное имя (до 100 символов).")
        return
    
    await state.update_data(name=name)
    await state.set_state(CreateTestStates.waiting_for_height)
    await message.answer(
        "📏 <b>Вопрос 2 из 4:</b>\n"
        "Какой у тебя рост?",
        parse_mode="HTML",
        reply_markup=get_height_keyboard()
    )


@router.message(CreateTestStates.waiting_for_height, F.text.in_(["140-159", "160-179", "180-199", "200+"]))
async def process_height(message: Message, state: FSMContext):
    """Обработка роста"""
    height = message.text
    await state.update_data(height_range=height)
    await state.set_state(CreateTestStates.waiting_for_eye_color)
    await message.answer(
        "👁️ <b>Вопрос 3 из 4:</b>\n"
        "Какого цвета у тебя глаза?",
        parse_mode="HTML",
        reply_markup=get_eye_color_keyboard()
    )


@router.message(CreateTestStates.waiting_for_height)
async def process_height_invalid(message: Message):
    """Некорректный выбор роста"""
    await message.answer("Пожалуйста, выбери один из предложенных вариантов роста.")


@router.message(CreateTestStates.waiting_for_eye_color, F.text.in_(["Карие", "Голубые", "Зелёные", "Серые"]))
async def process_eye_color(message: Message, state: FSMContext):
    """Обработка цвета глаз"""
    eye_color = message.text
    await state.update_data(eye_color=eye_color)
    await state.set_state(CreateTestStates.waiting_for_fear)
    await message.answer(
        "😰 <b>Вопрос 4 из 4:</b>\n"
        "Чего ты боишься больше всего?",
        parse_mode="HTML",
        reply_markup=get_fear_keyboard()
    )


@router.message(CreateTestStates.waiting_for_eye_color)
async def process_eye_color_invalid(message: Message):
    """Некорректный выбор цвета глаз"""
    await message.answer("Пожалуйста, выбери один из предложенных вариантов цвета глаз.")


@router.message(CreateTestStates.waiting_for_fear, F.text.in_(["Высоты", "Темноты", "Пауков", "Одиночества"]))
async def process_fear(message: Message, state: FSMContext):
    """Обработка страха и завершение создания теста"""
    fear = message.text
    data = await state.get_data()
    
    # Генерируем уникальный ID теста
    test_id = f"test_{uuid.uuid4().hex[:12]}"
    
    # Сохраняем тест в базу данных
    success = await db.create_test(
        test_id=test_id,
        creator_id=message.from_user.id,
        name=data['name'],
        height_range=data['height_range'],
        eye_color=data['eye_color'],
        fear=fear
    )
    
    if success:
        # Генерируем ссылку
        bot_info = await message.bot.get_me()
        bot_username = config.BOT_USERNAME or bot_info.username
        test_link = f"https://t.me/{bot_username}?start={test_id}"
        
        await message.answer(
            "✅ <b>Тест успешно создан!</b>\n\n"
            f"📎 <b>Твоя ссылка:</b>\n"
            f"{test_link}\n\n"
            "Отправь эту ссылку другу, чтобы он прошёл твой тест дружбы! 👇",
            parse_mode="HTML",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await message.answer(
            "❌ Произошла ошибка при создании теста. Попробуй ещё раз.",
            reply_markup=get_main_menu_keyboard()
        )
    
    await state.clear()


@router.message(CreateTestStates.waiting_for_fear)
async def process_fear_invalid(message: Message):
    """Некорректный выбор страха"""
    await message.answer("Пожалуйста, выбери один из предложенных вариантов.")

