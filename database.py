"""
Модуль для работы с базой данных
"""
import aiosqlite
from typing import Optional, List, Dict
from datetime import datetime
import config


class Database:
    """Класс для работы с базой данных SQLite"""
    
    def __init__(self, db_path: str = config.DATABASE_PATH):
        self.db_path = db_path
    
    async def init_db(self):
        """Инициализация базы данных - создание таблиц"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица пользователей
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_subscribed INTEGER DEFAULT 1
                )
            """)
            
            # Таблица тестов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tests (
                    test_id TEXT PRIMARY KEY,
                    creator_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    height_range TEXT,
                    eye_color TEXT,
                    fear TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (creator_id) REFERENCES users(user_id)
                )
            """)
            
            # Таблица ответов пользователей на тесты
            await db.execute("""
                CREATE TABLE IF NOT EXISTS test_answers (
                    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    test_id TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    name TEXT,
                    height_range TEXT,
                    eye_color TEXT,
                    fear TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (test_id) REFERENCES tests(test_id),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            """)
            
            await db.commit()
    
    async def add_user(self, user_id: int, username: Optional[str] = None, 
                      first_name: Optional[str] = None):
        """Добавление или обновление пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users (user_id, username, first_name, is_subscribed)
                VALUES (?, ?, ?, 1)
            """, (user_id, username, first_name))
            await db.commit()
    
    async def create_test(self, test_id: str, creator_id: int, name: str, 
                         height_range: str, eye_color: str, fear: str) -> bool:
        """Создание нового теста"""
        async with aiosqlite.connect(self.db_path) as db:
            try:
                await db.execute("""
                    INSERT INTO tests (test_id, creator_id, name, height_range, eye_color, fear)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (test_id, creator_id, name, height_range, eye_color, fear))
                await db.commit()
                return True
            except Exception as e:
                print(f"Error creating test: {e}")
                return False
    
    async def get_test(self, test_id: str) -> Optional[Dict]:
        """Получение теста по ID"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM tests WHERE test_id = ?
            """, (test_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None
    
    async def get_user_tests(self, user_id: int) -> List[Dict]:
        """Получение всех тестов пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM tests WHERE creator_id = ? ORDER BY created_at DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
    
    async def save_test_answer(self, test_id: str, user_id: int, name: str,
                               height_range: str, eye_color: str, fear: str):
        """Сохранение ответа пользователя на тест"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO test_answers (test_id, user_id, name, height_range, eye_color, fear)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (test_id, user_id, name, height_range, eye_color, fear))
            await db.commit()
    
    async def calculate_match_percentage(self, test_id: str, user_id: int) -> int:
        """Подсчет процента совпадений ответов с оригинальным тестом"""
        async with aiosqlite.connect(self.db_path) as db:
            # Получаем оригинальный тест
            test = await self.get_test(test_id)
            if not test:
                return 0
            
            # Получаем ответ пользователя
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM test_answers 
                WHERE test_id = ? AND user_id = ? 
                ORDER BY created_at DESC LIMIT 1
            """, (test_id, user_id)) as cursor:
                answer_row = await cursor.fetchone()
                if not answer_row:
                    return 0
                
                answer = dict(answer_row)
            
            # Сравниваем ответы
            matches = 0
            total = 4  # Всего 4 вопроса
            
            if answer.get('name', '').lower() == test.get('name', '').lower():
                matches += 1
            if answer.get('height_range') == test.get('height_range'):
                matches += 1
            if answer.get('eye_color') == test.get('eye_color'):
                matches += 1
            if answer.get('fear') == test.get('fear'):
                matches += 1
            
            percentage = int((matches / total) * 100)
            return percentage
    
    async def get_all_subscribed_users(self) -> List[int]:
        """Получение списка всех подписанных пользователей"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT user_id FROM users WHERE is_subscribed = 1
            """) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

