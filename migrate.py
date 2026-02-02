#!/usr/bin/env python3
import sqlite3
import os
from config import DB_NAME

def migrate_database():
    """Миграция существующей базы данных"""
    
    if not os.path.exists(DB_NAME):
        print(f"База данных {DB_NAME} не найдена.")
        return
    
    print(f" Начинаем миграцию базы данных {DB_NAME}...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Проверяем и добавляем недостающие колонки в user_stats
        cursor.execute("PRAGMA table_info(user_stats)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        print(f"Найдены колонки в user_stats: {column_names}")
        
        # Добавляем отсутствующие колонки
        if 'username' not in column_names:
            cursor.execute("ALTER TABLE user_stats ADD COLUMN username TEXT")
            print(" Добавлена колонка username")
        
        if 'first_name' not in column_names:
            cursor.execute("ALTER TABLE user_stats ADD COLUMN first_name TEXT")
            print(" Добавлена колонка first_name")
        
        if 'last_name' not in column_names:
            cursor.execute("ALTER TABLE user_stats ADD COLUMN last_name TEXT")
            print(" Добавлена колонка last_name")
        
        if 'last_quiz_date' not in column_names:
            cursor.execute("ALTER TABLE user_stats ADD COLUMN last_quiz_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            print(" Добавлена колонка last_quiz_date")
        
        conn.commit()
        print(" Миграция завершена успешно!")
        
    except Exception as e:
        print(f" Ошибка при миграции: {e}")
        conn.rollback()
    
    finally:
        conn.close()

def check_database_structure():
    """Проверка структуры базы данных"""
    
    if not os.path.exists(DB_NAME):
        print(f"База данных {DB_NAME} не найдена.")
        return
    
    print(f" Проверка структуры базы данных {DB_NAME}...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    try:
        # Получаем список всех таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Найдены таблицы: {[t[0] for t in tables]}")
        
        # Проверяем каждую таблицу
        for table in tables:
            table_name = table[0]
            print(f"\n Таблица: {table_name}")
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                print(f"  Колонка {col_id}: {col_name} ({col_type}) {'PRIMARY KEY' if pk else ''}")
    
    except Exception as e:
        print(f" Ошибка при проверке: {e}")
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Мигратор базы данных Python Quiz Bot")
    print("=" * 50)
    
    print("\n1. Проверить структуру базы данных")
    print("2. Выполнить миграцию")
    print("3. Выйти")
    
    choice = input("\nВыберите действие (1-3): ")
    
    if choice == "1":
        check_database_structure()
    elif choice == "2":
        migrate_database()
    elif choice == "3":
        print("Выход...")
    else:
        print("Неверный выбор")