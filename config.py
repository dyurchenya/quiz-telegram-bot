import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Токен бота из переменных окружения
API_TOKEN = os.getenv('BOT_TOKEN', '8558776620:AAFsVUVWabCbosd5xSe1RYS-o1PLx3brz5o')

# Настройки базы данных
DB_NAME = 'quiz_bot.db'

# Настройки логирования
LOG_LEVEL = 'INFO'