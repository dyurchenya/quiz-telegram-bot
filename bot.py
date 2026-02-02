import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import API_TOKEN, LOG_LEVEL
from database import Database
from handlers import register_handlers
import sys


# Настройка логирования
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('quiz_bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


async def main():
    # Проверка токена
    if not API_TOKEN:
        logger.error("Токен бота не найден! Проверьте файл .env")
        return
    
    logger.info("Запуск бота...")
    
    try:
        # Инициализация бота и диспетчера
        bot = Bot(token=API_TOKEN)
        dp = Dispatcher()
        
        # Инициализация базы данных
        logger.info("Инициализация базы данных...")
        db = Database()
        await db.create_tables()
        logger.info("База данных инициализирована")
        
        # Регистрация хендлеров
        logger.info("Регистрация хендлеров...")
        register_handlers(dp)
        logger.info("Хендлеры зарегистрированы")
        
        # Запуск бота
        logger.info("Бот запущен и готов к работе!")
        logger.info("Логи будут сохраняться в quiz_bot.log")
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())