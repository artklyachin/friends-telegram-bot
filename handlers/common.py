"""
Обработчики общих команд и главного меню
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards import get_main_menu_keyboard
from database import Database

router = Router()
db = Database()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    import logging
    logger = logging.getLogger(__name__)
    
    await state.clear()
    
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Регистрируем пользователя
    await db.add_user(user_id, username, first_name)
    
    # Проверяем, есть ли параметр start (ссылка на тест)
    # При переходе по ссылке Telegram отправляет /start test_id
    if message.text:
        parts = message.text.split()
        if len(parts) > 1:
            test_id = parts[1]
            logger.info(f"User {user_id} started test with ID: {test_id}")
            # Запускаем прохождение теста
            from handlers.test_taking import start_test_taking
            try:
                await start_test_taking(message, state, test_id)
                return
            except Exception as e:
                logger.error(f"Error starting test: {e}", exc_info=True)
                await message.answer(
                    "❌ Произошла ошибка при запуске теста. Попробуй ещё раз.",
                    reply_markup=get_main_menu_keyboard()
                )
                return
    
    # Обычное приветствие
    await message.answer(
        "👋 Привет! Я бот для создания тестов дружбы.\n\n"
        "Создай свой тест и отправь ссылку другу, чтобы проверить, насколько хорошо он тебя знает!",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "Информация")
async def cmd_info(message: Message):
    """Обработчик кнопки 'Информация'"""
    info_text = (
        "ℹ️ <b>Информация о боте</b>\n\n"
        "Этот бот позволяет создавать и проходить тесты дружбы.\n\n"
        "<b>Как это работает:</b>\n"
        "1. Создай тест, ответив на вопросы о себе\n"
        "2. Получи уникальную ссылку\n"
        "3. Отправь ссылку другу\n"
        "4. Друг проходит тест, отвечая на те же вопросы\n"
        "5. Узнай, насколько хорошо друг тебя знает!\n\n"
        "Используй меню для навигации."
    )
    await message.answer(info_text, parse_mode="HTML")


@router.message(F.text == "Мой тест")
async def cmd_my_tests(message: Message):
    """Показывает список тестов пользователя"""
    user_id = message.from_user.id
    tests = await db.get_user_tests(user_id)
    
    if not tests:
        await message.answer(
            "У тебя пока нет созданных тестов.\n"
            "Создай свой первый тест, нажав 'Создать тест'!"
        )
        return
    
    # Получаем username бота
    bot_info = await message.bot.get_me()
    bot_username = bot_info.username
    
    text = "📋 <b>Твои тесты:</b>\n\n"
    for test in tests:
        test_link = f"https://t.me/{bot_username}?start={test['test_id']}"
        text += f"• <b>{test['name']}</b>\n"
        text += f"  Ссылка: {test_link}\n\n"
    
    await message.answer(text, parse_mode="HTML")

