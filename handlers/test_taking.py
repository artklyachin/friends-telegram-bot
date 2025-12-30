"""
Обработчики для прохождения теста
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from states import TakeTestStates
from keyboards import (
    get_main_menu_keyboard, get_height_keyboard, 
    get_eye_color_keyboard, get_fear_keyboard, get_create_test_button
)
from database import Database

router = Router()
db = Database()


async def start_test_taking(message: Message, state: FSMContext, test_id: str):
    """Начало прохождения теста (вызывается из common.py)"""
    # Проверяем, существует ли тест
    test = await db.get_test(test_id)
    if not test:
        await message.answer(
            "❌ Тест не найден. Возможно, ссылка неверна или тест был удалён.",
            reply_markup=get_main_menu_keyboard()
        )
        return
    
    # Сохраняем test_id в состоянии
    await state.update_data(test_id=test_id)
    await state.set_state(TakeTestStates.waiting_for_name)
    
    await message.answer(
        "🎯 <b>Тест дружбы!</b>\n\n"
        "Твой друг создал тест, чтобы проверить, насколько хорошо ты его знаешь.\n\n"
        "📝 <b>Вопрос 1 из 4:</b>\n"
        "Как зовут твоего друга? (введи имя)",
        parse_mode="HTML",
        reply_markup=None
    )


@router.message(F.text == "Пройти тест")
async def cmd_take_test(message: Message, state: FSMContext):
    """Обработчик кнопки 'Пройти тест'"""
    await message.answer(
        "Чтобы пройти тест, тебе нужна ссылка от друга.\n\n"
        "Попроси друга отправить тебе ссылку на его тест дружбы!"
    )


@router.message(TakeTestStates.waiting_for_name)
async def process_taking_name(message: Message, state: FSMContext):
    """Обработка имени при прохождении теста"""
    name = message.text.strip()
    if not name or len(name) > 100:
        await message.answer("Пожалуйста, введи корректное имя (до 100 символов).")
        return
    
    await state.update_data(name=name)
    await state.set_state(TakeTestStates.waiting_for_height)
    await message.answer(
        "📏 <b>Вопрос 2 из 4:</b>\n"
        "Какой рост у твоего друга?",
        parse_mode="HTML",
        reply_markup=get_height_keyboard()
    )


@router.message(TakeTestStates.waiting_for_height, F.text.in_(["140-159", "160-179", "180-199", "200+"]))
async def process_taking_height(message: Message, state: FSMContext):
    """Обработка роста при прохождении теста"""
    height = message.text
    await state.update_data(height_range=height)
    await state.set_state(TakeTestStates.waiting_for_eye_color)
    await message.answer(
        "👁️ <b>Вопрос 3 из 4:</b>\n"
        "Какого цвета глаза у твоего друга?",
        parse_mode="HTML",
        reply_markup=get_eye_color_keyboard()
    )


@router.message(TakeTestStates.waiting_for_height)
async def process_taking_height_invalid(message: Message):
    """Некорректный выбор роста"""
    await message.answer("Пожалуйста, выбери один из предложенных вариантов роста.")


@router.message(TakeTestStates.waiting_for_eye_color, F.text.in_(["Карие", "Голубые", "Зелёные", "Серые"]))
async def process_taking_eye_color(message: Message, state: FSMContext):
    """Обработка цвета глаз при прохождении теста"""
    eye_color = message.text
    await state.update_data(eye_color=eye_color)
    await state.set_state(TakeTestStates.waiting_for_fear)
    await message.answer(
        "😰 <b>Вопрос 4 из 4:</b>\n"
        "Чего больше всего боится твой друг?",
        parse_mode="HTML",
        reply_markup=get_fear_keyboard()
    )


@router.message(TakeTestStates.waiting_for_eye_color)
async def process_taking_eye_color_invalid(message: Message):
    """Некорректный выбор цвета глаз"""
    await message.answer("Пожалуйста, выбери один из предложенных вариантов цвета глаз.")


@router.message(TakeTestStates.waiting_for_fear, F.text.in_(["Высоты", "Темноты", "Пауков", "Одиночества"]))
async def process_taking_fear(message: Message, state: FSMContext):
    """Обработка страха и завершение прохождения теста"""
    fear = message.text
    data = await state.get_data()
    test_id = data.get('test_id')
    
    if not test_id:
        await message.answer("Ошибка: не найден ID теста.")
        await state.clear()
        return
    
    # Сохраняем ответы пользователя
    await db.save_test_answer(
        test_id=test_id,
        user_id=message.from_user.id,
        name=data['name'],
        height_range=data['height_range'],
        eye_color=data['eye_color'],
        fear=fear
    )
    
    # Подсчитываем процент совпадений
    percentage = await db.calculate_match_percentage(test_id, message.from_user.id)
    
    # Определяем количество правильных ответов
    test = await db.get_test(test_id)
    matches = 0
    if data['name'].lower() == test['name'].lower():
        matches += 1
    if data['height_range'] == test['height_range']:
        matches += 1
    if data['eye_color'] == test['eye_color']:
        matches += 1
    if fear == test['fear']:
        matches += 1
    
    # Формируем результат
    result_text = (
        f"🎉 <b>Результат теста!</b>\n\n"
        f"Ты угадал <b>{matches} из 4</b> — это <b>{percentage}%</b>\n\n"
    )
    
    if percentage == 100:
        result_text += "🌟 Отлично! Ты идеально знаешь своего друга!"
    elif percentage >= 75:
        result_text += "👍 Хорошо! Ты хорошо знаешь своего друга!"
    elif percentage >= 50:
        result_text += "😊 Неплохо! Но есть что улучшить."
    else:
        result_text += "🤔 Похоже, стоит лучше узнать своего друга!"
    
    await message.answer(
        result_text,
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard()
    )
    
    # Предлагаем создать свой тест
    await message.answer(
        "Хочешь создать свой тест дружбы?",
        reply_markup=get_create_test_button()
    )
    
    await state.clear()


@router.message(TakeTestStates.waiting_for_fear)
async def process_taking_fear_invalid(message: Message):
    """Некорректный выбор страха"""
    await message.answer("Пожалуйста, выбери один из предложенных вариантов.")


@router.callback_query(F.data == "create_test_after")
async def create_test_after_callback(callback: CallbackQuery, state: FSMContext):
    """Обработчик кнопки создания теста после прохождения"""
    await callback.answer()
    from handlers.test_creation import start_test_creation
    await start_test_creation(callback.message, state)

