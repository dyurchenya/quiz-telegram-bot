from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from quiz_content import quiz_data, get_total_questions, get_question_by_index, get_correct_answer, get_explanation
from keyboards import generate_options_keyboard, get_start_keyboard, get_stats_keyboard
from database import Database
import asyncio
import random

db = Database()


# Команда /start
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в Python Quiz Bot!\n\n"
        f"Проверьте свои знания Python с помощью нашего квиза!\n"
        f"Всего доступно вопросов: {get_total_questions()}\n\n"
        "Нажмите '🎮 Начать игру' чтобы начать!",
        reply_markup=get_start_keyboard()
    )


def generate_unique_questions(count: int = 10):
    """Генерирует список уникальных вопросов для квиза"""
    total_questions = get_total_questions()
    
    if count > total_questions:
        count = total_questions
    
    all_questions = list(range(total_questions))
    random.shuffle(all_questions)
    return all_questions[:count]


# Команда /quiz и кнопка "Начать игру"
async def cmd_quiz(message: Message):
    user_id = message.from_user.id
    
    try:
        # Генерируем уникальную последовательность вопросов
        question_sequence = generate_unique_questions(10)
        print(f"🎮 Начало квиза для user_id={user_id}, вопросов: {len(question_sequence)}")
        
        # Инициализируем квиз для пользователя
        await db.init_user_quiz(
            user_id=user_id,
            question_sequence=question_sequence,
            username=message.from_user.username or "",
            first_name=message.from_user.first_name or "",
            last_name=message.from_user.last_name or ""
        )
        
        await message.answer(
            f"🎮 Начинаем квиз!\n"
            f"Будет задано {len(question_sequence)} уникальных вопросов. Удачи! 🍀"
        )
        await send_question(message, user_id)
    except Exception as e:
        print(f"Ошибка при начале квиза: {e}")
        await message.answer("Произошла ошибка при начале квиза.")


async def send_question(message: types.Message, user_id: int):
    """Отправляет вопрос пользователю"""
    try:
        quiz_state = await db.get_quiz_state(user_id)
        
        if not quiz_state:
            await message.answer("Произошла ошибка. Начните квиз заново: /quiz")
            return
        
        current_index = quiz_state['question_index']
        question_sequence = quiz_state['current_questions']
        
        print(f"📝 Отправка вопроса {current_index + 1} из {len(question_sequence)} для user_id={user_id}")
        
        # Проверяем, не завершен ли квиз
        if current_index >= len(question_sequence):
            # Завершаем квиз
            await finish_quiz(message, user_id, quiz_state)
            return
        
        # Получаем текущий вопрос из последовательности
        question_id = question_sequence[current_index]
        question = get_question_by_index(question_id)
        
        if not question:
            await message.answer("Ошибка: вопрос не найден!")
            return
        
        await message.answer(
            f"Вопрос {current_index + 1}/{len(question_sequence)}:\n\n"
            f"{question['question']}",
            reply_markup=generate_options_keyboard(question_id)
        )
    except Exception as e:
        print(f"Ошибка при отправке вопроса: {e}")
        await message.answer("Произошла ошибка.")


async def finish_quiz(message: types.Message, user_id: int, quiz_state):
    """Завершает квиз и показывает результаты"""
    try:
        score = quiz_state.get('score', 0)
        question_sequence = quiz_state['current_questions']
        total_questions = len(question_sequence)
        
        print(f"🏁 Завершение квиза для user_id={user_id}, счет: {score}/{total_questions}")
        
        # Получаем текущую статистику перед обновлением
        old_stats = await db.get_user_stats(user_id)
        if old_stats:
            print(f"📊 Старая статистика: квизов={old_stats['total_quizzes']}, правильных={old_stats['total_correct']}")
        
        # Обновляем статистику
        await db.complete_quiz(user_id, score, total_questions)
        
        # Получаем обновленную статистику
        user_stats = await db.get_user_stats(user_id)
        
        # Формируем сообщение с результатами
        result_text = f"🏁 Квиз завершен!\n\n"
        result_text += f"📊 Ваш результат: {score}/{total_questions}\n"
        result_text += f"📈 Процент правильных ответов: {round(score/total_questions*100, 1)}%\n\n"
        
        # Добавляем оценку результата
        if score == total_questions:
            result_text += "🎉 Отличный результат! Вы знаток Python!\n"
        elif score >= total_questions * 0.7:
            result_text += "Хороший результат!\n"
        elif score >= total_questions * 0.5:
            result_text += "Неплохо, но есть куда расти!\n"
        else:
            result_text += "📚 Попробуйте еще раз, чтобы улучшить результат!\n"
        
        # Добавляем общую статистику
        if user_stats and user_stats['total_questions'] > 0:
            total_accuracy = (user_stats['total_correct'] / user_stats['total_questions'] * 100)
            result_text += f"\n📋 Ваша общая статистика:\n"
            result_text += f"• Всего квизов: {user_stats['total_quizzes']}\n"
            result_text += f"• Правильных ответов: {user_stats['total_correct']}/{user_stats['total_questions']}\n"
            result_text += f"• Лучший результат: {user_stats['best_score']}/10\n"
            result_text += f"• Общая точность: {round(total_accuracy, 1)}%\n"
            if user_stats['last_quiz']:
                result_text += f"• Последний квиз: {user_stats['last_quiz'][:16]}\n"
        
        result_text += f"\n🎮 Чтобы пройти еще раз, нажмите '🎮 Начать игру'"
        
        # Очищаем состояние квиза
        await db.clear_quiz_state(user_id)
        
        await message.answer(result_text, reply_markup=get_start_keyboard())
        
    except Exception as e:
        print(f"Ошибка при завершении квиза: {e}")
        import traceback
        traceback.print_exc()
        
        # Показываем хотя бы базовый результат
        score = quiz_state.get('score', 0)
        question_sequence = quiz_state['current_questions']
        await message.answer(
            f"🏁 Квиз завершен!\n"
            f"Ваш результат: {score}/{len(question_sequence)}\n"
            f"Произошла ошибка при сохранении статистики.",
            reply_markup=get_start_keyboard()
        )


# Обработка ответов
async def process_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    data = callback.data
    
    try:
        if data.startswith("answer_"):
            try:
                parts = data.split("_")
                if len(parts) >= 3:
                    answer_index = int(parts[1])
                    question_index = int(parts[2])
                else:
                    await callback.answer("Ошибка формата данных!")
                    return
            except ValueError:
                await callback.answer("Ошибка в данных!")
                return
            
            quiz_state = await db.get_quiz_state(user_id)
            if not quiz_state:
                await callback.answer("Квиз не начат!")
                return
            
            question = get_question_by_index(question_index)
            if not question:
                await callback.answer("Вопрос не найден!")
                return
            
            # Получаем выбранный и правильный ответы
            selected_text = question['options'][answer_index]
            correct_index = question['correct_option']
            correct_text = question['options'][correct_index]
            is_correct = answer_index == correct_index
            
            # Удаляем клавиатуру с кнопками
            try:
                await callback.bot.edit_message_reply_markup(
                    chat_id=user_id,
                    message_id=callback.message.message_id,
                    reply_markup=None
                )
            except Exception as e:
                print(f"Ошибка при удалении клавиатуры: {e}")
            
            # Отправляем сообщение с выбранным ответом
            await callback.message.answer(
                f"📝 Ваш ответ: \"{selected_text}\"\n"
                f"{'✅ Верно!' if is_correct else 'Неправильно'}"
            )
            
            # Если ответ неправильный, показываем правильный ответ с объяснением
            if not is_correct:
                explanation = get_explanation(question_index)
                explanation_text = f"📚 Правильный ответ: \"{correct_text}\""
                if explanation:
                    explanation_text += f"\n{explanation}"
                await callback.message.answer(explanation_text)
            
            # Обновляем счет
            current_score = quiz_state.get('score', 0)
            new_score = current_score + (1 if is_correct else 0)
            
            # Обновляем состояние
            next_question_index = quiz_state['question_index'] + 1
            await db.update_quiz_state(user_id, next_question_index, new_score)
            
            # Небольшая задержка перед следующим вопросом
            await asyncio.sleep(1)
            
            # Отправляем следующий вопрос или завершаем квиз
            await send_question(callback.message, user_id)
            await callback.answer()
    except Exception as e:
        print(f"Ошибка при обработке ответа: {e}")
        await callback.answer("Произошла ошибка. Попробуйте еще раз.")


# Статистика пользователя
async def cmd_stats(message: Message):
    user_id = message.from_user.id
    
    try:
        stats = await db.get_user_stats(user_id)
        
        if stats and stats['total_questions'] > 0:
            accuracy = (stats['total_correct'] / stats['total_questions']) * 100
            
            response_text = (
                f"📊 Ваша статистика:\n\n"
                f"👤 Пользователь: {stats.get('first_name', '')} {stats.get('last_name', '')}\n"
                f"   @{stats.get('username', 'нет username')}\n\n"
                f"📈 Общая статистика:\n"
                f"• Количество квизов: {stats['total_quizzes']}\n"
                f"• Всего вопросов: {stats['total_questions']}\n"
                f"• Правильных ответов: {stats['total_correct']}\n"
                f"• Лучший результат: {stats['best_score']}/10\n"
                f"• Общая точность: {round(accuracy, 1)}%\n"
                f"• Последний квиз: {stats.get('last_quiz', 'неизвестно')}\n"
            )
            
            # Получаем результат последнего квиза
            last_quiz = await db.get_last_quiz_result(user_id)
            if last_quiz:
                last_accuracy = (last_quiz['score'] / last_quiz['total_questions'] * 100) if last_quiz['total_questions'] > 0 else 0
                response_text += (
                    f"\n📅 Последний квиз:\n"
                    f"• Результат: {last_quiz['score']}/{last_quiz['total_questions']}\n"
                    f"• Точность: {round(last_accuracy, 1)}%\n"
                )
            
            await message.answer(response_text, reply_markup=get_stats_keyboard())
        else:
            await message.answer(
                "📊 Вы еще не проходили квизы!\n"
                "Нажмите '🎮 Начать игру' чтобы проверить свои знания."
            )
    except Exception as e:
        print(f"Ошибка при получении статистики: {e}")
        await message.answer("Ошибка при получении статистики.")


# Топ игроков
async def cmd_top(message: Message):
    try:
        top_players = await db.get_top_players(10)
        
        if not top_players:
            await message.answer("📊 Пока нет статистики игроков.")
            return
        
        top_text = "🏆 Топ 10 игроков:\n\n"
        
        for i, player in enumerate(top_players, 1):
            # Формируем имя игрока
            if player['first_name'] and player['last_name']:
                name = f"{player['first_name']} {player['last_name']}"
            elif player['first_name']:
                name = player['first_name']
            elif player['username']:
                name = f"@{player['username']}"
            else:
                name = f"Игрок {player['user_id']}"
            
            # Добавляем медальки для первых трех мест
            medal = ""
            if i == 1:
                medal = "🥇 "
            elif i == 2:
                medal = "🥈 "
            elif i == 3:
                medal = "🥉 "
            
            top_text += (
                f"{medal}{i}. {name}\n"
                f"   Квизов: {player['total_quizzes']} | "
                f"Лучший: {player['best_score']}/10 | "
                f"Точность: {player['accuracy']}%\n"
            )
        
        top_text += "\n🎮 Пройдите квиз, чтобы попасть в топ!"
        
        await message.answer(top_text)
    except Exception as e:
        print(f"Ошибка при получении топа игроков: {e}")
        await message.answer("Ошибка при получении топа игроков.")


# Правила
async def cmd_rules(message: Message):
    await message.answer(
        "📋 Правила квиза:\n\n"
        "1. Каждый квиз состоит из 10 случайных вопросов\n"
        "2. Вопросы не повторяются в течение одного квиза\n"
        "3. У каждого вопроса 4 варианта ответа\n"
        "4. Выберите один правильный вариант\n"
        "5. После каждого ответа вы увидите свой выбор и результат\n"
        "6. В конце квиза увидите детальную статистику\n\n"
        "Цель: проверить и улучшить свои знания Python!\n\n"
        "Удачи!"
    )


# Главное меню
async def cmd_menu(message: Message):
    await message.answer(
        "🏠 Главное меню",
        reply_markup=get_start_keyboard()
    )


# Отмена квиза
async def cmd_cancel(message: Message):
    user_id = message.from_user.id
    
    try:
        # Проверяем, есть ли активный квиз
        quiz_state = await db.get_quiz_state(user_id)
        
        if quiz_state and quiz_state['completed'] == 0:
            # Очищаем состояние квиза
            await db.clear_quiz_state(user_id)
            await message.answer(
                "Квиз отменен.\n"
                "Вы можете начать новый квиз, нажав '🎮 Начать игру'",
                reply_markup=get_start_keyboard()
            )
        else:
            await message.answer(
                "У вас нет активного квиза.\n"
                "Начните новый квиз, нажав '🎮 Начать игру'",
                reply_markup=get_start_keyboard()
            )
    except Exception as e:
        print(f"Ошибка при отмене квиза: {e}")
        await message.answer("Ошибка при отмене квиза.")


# Регистрация хендлеров
def register_handlers(dp):
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(cmd_quiz, F.text == "🎮 Начать игру")
    dp.message.register(cmd_quiz, Command("quiz"))
    dp.message.register(cmd_stats, F.text == "📊 Моя статистика")
    dp.message.register(cmd_stats, Command("stats"))
    dp.message.register(cmd_top, F.text == "🏆 Топ игроков")
    dp.message.register(cmd_top, Command("top"))
    dp.message.register(cmd_rules, F.text == "📋 Правила")
    dp.message.register(cmd_rules, Command("rules"))
    dp.message.register(cmd_menu, F.text == "🏠 Главное меню")
    dp.message.register(cmd_menu, Command("menu"))
    dp.message.register(cmd_cancel, F.text == "❌ Отмена квиза")
    dp.message.register(cmd_cancel, Command("cancel"))
    dp.callback_query.register(process_answer, F.data.startswith("answer_"))