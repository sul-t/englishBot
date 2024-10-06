import sqlite3, random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


connect = sqlite3.connect('./english.db')
cursor = connect.cursor()


def generate_word_id(bilet):
    range_random = bilet * 50

    if bilet == 0:
        right_word_id = random.randint(1, 9998)
    elif bilet == 200:
        right_word_id = random.randint(range_random - 49, range_random - 2)
    else:
        right_word_id = random.randint(range_random - 49, range_random)

    return right_word_id


async def generate_words(user_id):
    keyboard = InlineKeyboardBuilder()

    bilet = cursor.execute('select bilet from users where user_id = ?', (user_id,)).fetchone()[0]

    right_word_id = generate_word_id(bilet)

    word_en, word_en_id, part_of_speech = cursor.execute('select word, id, part_of_speech from words where id = ?', (right_word_id,)).fetchone()
    translations = cursor.execute('select translation from translations where word_id = ?', (right_word_id,)).fetchall()
    index = random.randint(0, len(translations) - 1) if len(translations) != 1 else 0
    translation = translations[index][0]

    answers = set([translation])


    for i in range(3):
        bad_word_id = 0

        while True:
            bad_word_id = generate_word_id(bilet)

            if bad_word_id not in answers:
                break
            
        words_ru = cursor.execute('select translation from translations where word_id = ?', (bad_word_id,)).fetchall()
        index = random.randint(0, len(words_ru) - 1) if len(words_ru) != 1 else 0
        word_ru = words_ru[index][0]

        answers.add(word_ru)


    answers = list(answers)

    random.shuffle(answers)

    answers.append('Не знаю')

    for row in answers:
        keyboard.add(InlineKeyboardButton(text=row, callback_data=row))

    return word_en_id, word_en, part_of_speech, keyboard.adjust(2).as_markup()


def reply_keyboard():
    button = [
        [KeyboardButton(text='Билет'), KeyboardButton(text='Режим')]
    ]

    keyboard = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)

    return keyboard