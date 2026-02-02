import aiosqlite
import json
import asyncio
from config import DB_NAME


class Database:
    def __init__(self, db_name: str = DB_NAME):
        self.db_name = db_name
        self._lock = asyncio.Lock()
    
    async def create_tables(self):
        """Создание таблиц базы данных"""
        async with self._lock:
            async with aiosqlite.connect(self.db_name) as db:
                # Включаем поддержку внешних ключей
                await db.execute("PRAGMA foreign_keys = ON")
                await db.execute("PRAGMA journal_mode=WAL")
                await db.execute("PRAGMA synchronous=NORMAL")
                
                # Таблица состояния квиза
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS quiz_state (
                        user_id INTEGER PRIMARY KEY,
                        question_index INTEGER DEFAULT 0,
                        score INTEGER DEFAULT 0,
                        completed INTEGER DEFAULT 0,
                        used_questions TEXT DEFAULT '[]',
                        current_questions TEXT DEFAULT '[]'
                    )
                ''')
                
                # Таблица статистики пользователей
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS user_stats (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        total_quizzes INTEGER DEFAULT 0,
                        total_correct INTEGER DEFAULT 0,
                        total_questions INTEGER DEFAULT 0,
                        best_score INTEGER DEFAULT 0,
                        last_quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Таблица истории квизов
                await db.execute('''
                    CREATE TABLE IF NOT EXISTS quiz_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        score INTEGER,
                        total_questions INTEGER,
                        quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES user_stats (user_id)
                    )
                ''')
                
                await db.commit()
                print("✅ Таблицы базы данных созданы успешно")
                
                # Проверяем и добавляем отсутствующие колонки
                await self._migrate_database(db)
    
    async def _migrate_database(self, db):
        """Миграция базы данных - добавление отсутствующих колонок"""
        try:
            # Проверяем существование колонок в user_stats
            async with db.execute("PRAGMA table_info(user_stats)") as cursor:
                columns = await cursor.fetchall()
                column_names = [col[1] for col in columns]
                
                # Добавляем отсутствующие колонки
                if 'username' not in column_names:
                    await db.execute("ALTER TABLE user_stats ADD COLUMN username TEXT")
                    print("✅ Добавлена колонка username в user_stats")
                
                if 'first_name' not in column_names:
                    await db.execute("ALTER TABLE user_stats ADD COLUMN first_name TEXT")
                    print("✅ Добавлена колонка first_name в user_stats")
                
                if 'last_name' not in column_names:
                    await db.execute("ALTER TABLE user_stats ADD COLUMN last_name TEXT")
                    print("✅ Добавлена колонка last_name в user_stats")
                
                if 'last_quiz_date' not in column_names:
                    await db.execute("ALTER TABLE user_stats ADD COLUMN last_quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    print("✅ Добавлена колонка last_quiz_date в user_stats")
                
                await db.commit()
        except Exception as e:
            print(f"⚠️ Ошибка при миграции базы данных: {e}")
    
    async def get_quiz_state(self, user_id: int):
        """Получить состояние квиза для пользователя"""
        async with self._lock:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute(
                    'SELECT question_index, score, completed, used_questions, current_questions FROM quiz_state WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    result = await cursor.fetchone()
                    if result:
                        try:
                            used_questions = json.loads(result[3]) if result[3] else []
                        except:
                            used_questions = []
                        
                        try:
                            current_questions = json.loads(result[4]) if result[4] else []
                        except:
                            current_questions = []
                        
                        return {
                            'question_index': result[0],
                            'score': result[1],
                            'completed': result[2],
                            'used_questions': used_questions,
                            'current_questions': current_questions
                        }
                    return None
    
    async def init_user_quiz(self, user_id: int, question_sequence: list, 
                            username: str = "", first_name: str = "", last_name: str = ""):
        """Инициализировать новый квиз для пользователя"""
        async with self._lock:
            async with aiosqlite.connect(self.db_name) as db:
                # Сначала проверяем, существует ли пользователь
                async with db.execute(
                    'SELECT user_id FROM user_stats WHERE user_id = ?',
                    (user_id,)
                ) as cursor:
                    user_exists = await cursor.fetchone()
                
                if not user_exists:
                    # Создаем новую запись пользователя
                    await db.execute('''
                        INSERT INTO user_stats 
                        (user_id, username, first_name, last_name, total_quizzes, total_correct, total_questions, best_score) 
                        VALUES (?, ?, ?, ?, 0, 0, 0, 0)
                    ''', (user_id, username or "", first_name or "", last_name or ""))
                    print(f"👤 Создан новый пользователь: user_id={user_id}")
                else:
                    # Обновляем только имя пользователя, если оно изменилось
                    await db.execute('''
                        UPDATE user_stats 
                        SET username = COALESCE(?, username),
                            first_name = COALESCE(?, first_name),
                            last_name = COALESCE(?, last_name)
                        WHERE user_id = ?
                    ''', (username or "", first_name or "", last_name or "", user_id))
                
                # Инициализируем состояние квиза
                await db.execute(
                    '''INSERT OR REPLACE INTO quiz_state 
                       (user_id, question_index, score, completed, used_questions, current_questions) 
                       VALUES (?, 0, 0, 0, '[]', ?)''',
                    (user_id, json.dumps(question_sequence))
                )
                
                # Создаем запись в истории
                await db.execute(
                    '''INSERT INTO quiz_history (user_id, score, total_questions, quiz_date)
                       VALUES (?, 0, ?, CURRENT_TIMESTAMP)''',
                    (user_id, len(question_sequence))
                )
                
                await db.commit()
    
    async def update_quiz_state(self, user_id: int, question_index: int, score: int = None):
        """Обновить состояние квиза"""
        async with self._lock:
            async with aiosqlite.connect(self.db_name) as db:
                if score is not None:
                    await db.execute(
                        'UPDATE quiz_state SET question_index = ?, score = ? WHERE user_id = ?',
                        (question_index, score, user_id)
                    )
                else:
                    await db.execute(
                        'UPDATE quiz_state SET question_index = ? WHERE user_id = ?',
                        (question_index, user_id)
                    )
                await db.commit()
    
    async def complete_quiz(self, user_id: int, score: int, total_questions: int):
        """Завершить квиз и обновить статистику"""
        async with self._lock:
            async with aiosqlite.connect(self.db_name) as db:
                try:
                    # Получаем текущую статистику пользователя
                    async with db.execute(
                        'SELECT total_quizzes, total_correct, total_questions, best_score FROM user_stats WHERE user_id = ?',
                        (user_id,)
                    ) as cursor:
                        stats = await cursor.fetchone()
                    
                    if stats:
                        # Вычисляем новые значения статистики
                        current_total_quizzes = stats[0]
                        current_total_correct = stats[1]
                        current_total_questions = stats[2]
                        current_best_score = stats[3]
                        
                        new_total_quizzes = current_total_quizzes + 1
                        new_total_correct = current_total_correct + score
                        new_total_questions = current_total_questions + total_questions
                        new_best_score = max(current_best_score, score)
                        
                        print(f"📊 Обновление статистики: user_id={user_id}, "
                              f"было квизов={current_total_quizzes}, теперь={new_total_quizzes}, "
                              f"было правильных={current_total_correct}, добавилось={score}")
                        
                        # Обновляем статистику пользователя
                        await db.execute('''
                            UPDATE user_stats 
                            SET total_quizzes = ?, 
                                total_correct = ?, 
                                total_questions = ?, 
                                best_score = ?,
                                last_quiz_date = CURRENT_TIMESTAMP
                            WHERE user_id = ?
                        ''', (new_total_quizzes, new_total_correct, new_total_questions, new_best_score, user_id))
                    else:
                        # Создаем новую запись статистики
                        await db.execute('''
                            INSERT INTO user_stats 
                            (user_id, total_quizzes, total_correct, total_questions, best_score, last_quiz_date)
                            VALUES (?, 1, ?, ?, ?, CURRENT_TIMESTAMP)
                        ''', (user_id, score, total_questions, score))
                        print(f"📊 Создана новая запись статистики для user_id={user_id}")
                    
                    # Обновляем результат последнего квиза в истории
                    await db.execute('''
                        UPDATE quiz_history 
                        SET score = ?, quiz_date = CURRENT_TIMESTAMP
                        WHERE id = (
                            SELECT id FROM quiz_history 
                            WHERE user_id = ? 
                            ORDER BY quiz_date DESC 
                            LIMIT 1
                        )
                    ''', (score, user_id))
                    
                    # Отмечаем квиз как завершенный
                    await db.execute(
                        'UPDATE quiz_state SET completed = 1 WHERE user_id = ?',
                        (user_id,)
                    )
                    
                    await db.commit()
                    print(f"✅ Статистика успешно обновлена для user_id={user_id}")
                    
                except Exception as e:
                    print(f"❌ Ошибка при обновлении статистики: {e}")
                    import traceback
                    traceback.print_exc()
                    raise e
    
    async def get_user_stats(self, user_id: int):
        """Получить статистику пользователя"""
        async with self._lock:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute(
                    '''SELECT username, first_name, last_name, total_quizzes, 
                       total_correct, total_questions, best_score,
                       datetime(last_quiz_date) as last_quiz
                       FROM user_stats WHERE user_id = ?''',
                    (user_id,)
                ) as cursor:
                    result = await cursor.fetchone()
                    if result:
                        return {
                            'username': result[0],
                            'first_name': result[1],
                            'last_name': result[2],
                            'total_quizzes': result[3],
                            'total_correct': result[4],
                            'total_questions': result[5],
                            'best_score': result[6],
                            'last_quiz': result[7]
                        }
                    return None
    
    async def get_last_quiz_result(self, user_id: int):
        """Получить результат последнего квиза"""
        async with self._lock:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute('''
                    SELECT score, total_questions, datetime(quiz_date) as quiz_date
                    FROM quiz_history 
                    WHERE user_id = ? 
                    ORDER BY quiz_date DESC 
                    LIMIT 1
                ''', (user_id,)) as cursor:
                    result = await cursor.fetchone()
                    if result:
                        return {
                            'score': result[0],
                            'total_questions': result[1],
                            'quiz_date': result[2]
                        }
                    return None
    
    async def get_top_players(self, limit: int = 10):
        """Получить топ игроков"""
        async with self._lock:
            async with aiosqlite.connect(self.db_name) as db:
                async with db.execute('''
                    SELECT user_id, username, first_name, last_name, 
                           total_quizzes, best_score, total_correct, total_questions
                    FROM user_stats 
                    WHERE total_quizzes > 0
                    ORDER BY best_score DESC, total_correct DESC, total_quizzes DESC
                    LIMIT ?
                ''', (limit,)) as cursor:
                    results = await cursor.fetchall()
                    players = []
                    for row in results:
                        accuracy = (row[6] / row[7] * 100) if row[7] > 0 else 0
                        players.append({
                            'user_id': row[0],
                            'username': row[1],
                            'first_name': row[2],
                            'last_name': row[3],
                            'total_quizzes': row[4],
                            'best_score': row[5],
                            'accuracy': round(accuracy, 1)
                        })
                    return players
    
    async def clear_quiz_state(self, user_id: int):
        """Очистить состояние квиза"""
        async with self._lock:
            async with aiosqlite.connect(self.db_name) as db:
                await db.execute(
                    'DELETE FROM quiz_state WHERE user_id = ?',
                    (user_id,)
                )
                await db.commit()