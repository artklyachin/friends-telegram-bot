"""
Модуль для рассылки сообщений подписчикам
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot
from database import Database
import config
import logging

logger = logging.getLogger(__name__)


class BroadcastScheduler:
    """Класс для управления рассылкой сообщений"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.db = Database()
    
    async def broadcast_message(self):
        """Отправка сообщения всем подписчикам"""
        try:
            users = await self.db.get_all_subscribed_users()
            logger.info(f"Starting broadcast to {len(users)} users")
            
            success_count = 0
            error_count = 0
            
            for user_id in users:
                try:
                    await self.bot.send_message(
                        user_id,
                        config.BROADCAST_MESSAGE,
                        reply_markup=None
                    )
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")
                    error_count += 1
            
            logger.info(f"Broadcast completed: {success_count} sent, {error_count} errors")
        except Exception as e:
            logger.error(f"Error in broadcast_message: {e}")
    
    def start(self):
        """Запуск планировщика рассылки"""
        # Добавляем задачу на выполнение каждый час
        self.scheduler.add_job(
            self.broadcast_message,
            trigger=IntervalTrigger(seconds=config.BROADCAST_INTERVAL),
            id='broadcast_job',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("Broadcast scheduler started")
    
    def shutdown(self):
        """Остановка планировщика"""
        self.scheduler.shutdown()
        logger.info("Broadcast scheduler stopped")

