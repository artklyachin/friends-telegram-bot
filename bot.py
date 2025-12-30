"""
Главный файл для запуска бота
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

import config
from database import Database
from handlers import common, test_creation, test_taking
from scheduler import BroadcastScheduler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    
    # Проверка токена
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Создайте файл .env и добавьте BOT_TOKEN=your_token")
        return
    
    # Инициализация бота и диспетчера
    bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация роутеров
    # Важно: обработчики состояний должны быть зарегистрированы перед общими обработчиками
    # чтобы они имели приоритет при обработке сообщений
    dp.include_router(test_taking.router)
    dp.include_router(test_creation.router)
    dp.include_router(common.router)
    
    # Инициализация базы данных
    db = Database()
    await db.init_db()
    logger.info("Database initialized")
    
    # Запуск планировщика рассылки
    scheduler = BroadcastScheduler(bot)
    scheduler.start()
    logger.info("Broadcast scheduler started")
    
    try:
        # Запуск бота
        logger.info("Bot starting...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Error in main: {e}")
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

