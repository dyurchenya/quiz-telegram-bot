import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import API_TOKEN, DB_NAME
from database import create_table
from handlers import cmd_start, cmd_quiz, right_answer, wrong_answer

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Объект бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Регистрация хэндлеров
dp.message.register(cmd_start, Command("start"))
dp.message.register(cmd_quiz, F.text=="Начать игру")
dp.message.register(cmd_quiz, Command("quiz"))
dp.callback_query.register(right_answer, F.data == "right_answer")
dp.callback_query.register(wrong_answer, F.data == "wrong_answer")

async def main():
    # Запускаем создание таблицы базы данных
    await create_table(DB_NAME)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())