quiz_data = [
    {
        'question': 'Что такое Python?',
        'options': [
            'Язык программирования',
            'Тип данных', 
            'Музыкальный инструмент',
            'Змея на английском'
        ],
        'correct_option': 0,
        'explanation': 'Python - это высокоуровневый язык программирования общего назначения.'
    },
    {
        'question': 'Какой тип данных используется для хранения целых чисел?',
        'options': [
            'int',
            'float', 
            'str',
            'bool'
        ],
        'correct_option': 0,
        'explanation': 'int (integer) используется для хранения целых чисел.'
    },
    {
        'question': 'Что выведет код: print(3 + 2 * 2)?',
        'options': [
            '10',
            '7',
            '12',
            'Ошибку'
        ],
        'correct_option': 1,
        'explanation': 'Сначала выполняется умножение (2*2=4), затем сложение (3+4=7).'
    },
    {
        'question': 'Какой оператор используется для получения остатка от деления?',
        'options': [
            '%',
            '//',
            '/',
            '**'
        ],
        'correct_option': 0,
        'explanation': 'Оператор % возвращает остаток от деления.'
    },
    {
        'question': 'Что такое список (list) в Python?',
        'options': [
            'Изменяемая последовательность элементов',
            'Неизменяемая последовательность элементов',
            'Словарь с ключами и значениями',
            'Множество уникальных элементов'
        ],
        'correct_option': 0,
        'explanation': 'Список (list) - это изменяемая упорядоченная коллекция элементов.'
    },
    {
        'question': 'Как добавить элемент в конец списка?',
        'options': [
            'append()',
            'add()',
            'insert()',
            'push()'
        ],
        'correct_option': 0,
        'explanation': 'Метод append() добавляет элемент в конец списка.'
    },
    {
        'question': 'Что такое кортеж (tuple)?',
        'options': [
            'Неизменяемая последовательность элементов',
            'Изменяемая последовательность элементов',
            'Словарь без ключей',
            'Список без индексов'
        ],
        'correct_option': 0,
        'explanation': 'Кортеж (tuple) - это неизменяемая упорядоченная коллекция элементов.'
    },
    {
        'question': 'Как создать пустой словарь?',
        'options': [
            '{} или dict()',
            '[]',
            '()',
            'set()'
        ],
        'correct_option': 0,
        'explanation': 'Пустой словарь создается с помощью {} или функции dict().'
    },
    {
        'question': 'Что делает функция len()?',
        'options': [
            'Возвращает длину объекта',
            'Возвращает тип объекта',
            'Округляет число',
            'Преобразует в строку'
        ],
        'correct_option': 0,
        'explanation': 'Функция len() возвращает количество элементов в объекте.'
    },
    {
        'question': 'Какой из этих циклов является бесконечным?',
        'options': [
            'while True:',
            'for i in range(10):',
            'for item in list:',
            'while x < 10:'
        ],
        'correct_option': 0,
        'explanation': 'while True: будет выполняться бесконечно, пока его не прервут.'
    },
    {
        'question': 'Что такое lambda-функция?',
        'options': [
            'Анонимная функция',
            'Именованная функция',
            'Встроенная функция',
            'Рекурсивная функция'
        ],
        'correct_option': 0,
        'explanation': 'Lambda-функция - это анонимная функция, определяемая с помощью ключевого слова lambda.'
    },
    {
        'question': 'Как импортировать модуль math?',
        'options': [
            'import math',
            'from math import *',
            'include math',
            'require math'
        ],
        'correct_option': 0,
        'explanation': 'Модуль импортируется с помощью ключевого слова import.'
    },
    {
        'question': 'Что такое PEP 8?',
        'options': [
            'Руководство по стилю кода Python',
            'Новая версия Python',
            'Библиотека для работы с данными',
            'Протокол передачи данных'
        ],
        'correct_option': 0,
        'explanation': 'PEP 8 - это руководство по написанию читаемого кода на Python.'
    },
    {
        'question': 'Какой символ используется для комментариев в Python?',
        'options': [
            '#',
            '//',
            '/*',
            '--'
        ],
        'correct_option': 0,
        'explanation': 'В Python для однострочных комментариев используется символ #.'
    },
    {
        'question': 'Что делает оператор **?',
        'options': [
            'Возведение в степень',
            'Умножение',
            'Двойное сложение',
            'Комментарий'
        ],
        'correct_option': 0,
        'explanation': 'Оператор ** используется для возведения в степень.'
    }
]

# Функция для получения случайных вопросов
def get_random_questions(count=10):
    """Возвращает указанное количество случайных вопросов"""
    import random
    if count > len(quiz_data):
        count = len(quiz_data)
    return random.sample(quiz_data, count)

# Функция для получения вопроса по индексу
def get_question_by_index(index):
    """Возвращает вопрос по указанному индексу"""
    if 0 <= index < len(quiz_data):
        return quiz_data[index]
    return None

# Функция для подсчета общего количества вопросов
def get_total_questions():
    """Возвращает общее количество вопросов"""
    return len(quiz_data)

# Функция для проверки правильности ответа
def check_answer(question_index, selected_option):
    """Проверяет правильность выбранного варианта"""
    if 0 <= question_index < len(quiz_data):
        question = quiz_data[question_index]
        return selected_option == question['correct_option']
    return False

# Функция для получения правильного ответа
def get_correct_answer(question_index):
    """Возвращает правильный ответ для вопроса"""
    if 0 <= question_index < len(quiz_data):
        question = quiz_data[question_index]
        return question['options'][question['correct_option']]
    return None

# Функция для получения объяснения
def get_explanation(question_index):
    """Возвращает объяснение для вопроса"""
    if 0 <= question_index < len(quiz_data):
        return quiz_data[question_index].get('explanation', '')
    return ''