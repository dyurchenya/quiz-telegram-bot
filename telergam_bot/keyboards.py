from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types
from quiz_content import get_question_by_index


def generate_options_keyboard(question_index: int):
    """Генерирует клавиатуру с вариантами ответов для текущего вопроса"""
    builder = InlineKeyboardBuilder()
    
    question = get_question_by_index(question_index)
    if not question:
        return None
    
    answer_options = question['options']
    
    for i, option in enumerate(answer_options):
        # Добавляем эмодзи для лучшей визуализации
        emoji = ["🅰", "🅱", "🅲", "🅳"][i] if i < 4 else str(i+1)
        builder.add(types.InlineKeyboardButton(
            text=f"{emoji} {option}",
            callback_data=f"answer_{i}_{question_index}")
        )
    
    builder.adjust(1)
    return builder.as_markup()


def get_start_keyboard():
    """Клавиатура для стартового меню"""
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="🎮 Начать игру"))
    builder.add(types.KeyboardButton(text="📊 Моя статистика"))
    builder.add(types.KeyboardButton(text="🏆 Топ игроков"))
    builder.add(types.KeyboardButton(text="📋 Правила"))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_stats_keyboard():
    """Клавиатура для меню статистики"""
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="🎮 Начать игру"))
    builder.add(types.KeyboardButton(text="🏠 Главное меню"))
    return builder.as_markup(resize_keyboard=True)