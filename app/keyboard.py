import sqlite3, random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


connect = sqlite3.connect('./english.db')
cursor = connect.cursor()


async def generate_words(user_id):
    keyboard = InlineKeyboardBuilder()

    row = cursor.execute('select bilet from users where user_id = ?', (user_id,)).fetchone()

    if row is None:
        bilet = -1
    else:
        bilet = row[0]

    if bilet == -1:
        right_word_id = random.randint(1, 9998)
    else:
        right_word_id = random.randint(bilet, bilet + 50)


    word_en, word_en_id, part_of_speech = cursor.execute('select word, id, part_of_speech from words where id = ?', (right_word_id,)).fetchone()
    translations = cursor.execute('select translation from translations where word_id = ?', (right_word_id,)).fetchall()
    translation = translations[random.randint(0, len(translations) - 1)][0]

    answers = set([translation])


    for i in range(3):
        bad_word_id = 0

        while True:
            if bilet == -1:
                bad_word_id = random.randint(1, 9998)
            else:
                bad_word_id = random.randint(bilet, bilet + 50)

            if bad_word_id not in answers:
                break
            
        words_ru = cursor.execute('select translation from translations where word_id = ?', (bad_word_id,)).fetchall()
        word_ru = words_ru[random.randint(0, len(words_ru) - 1)][0]

        answers.add(word_ru)


    answers = list(answers)

    random.shuffle(answers)

    answers.append('Не знаю')

    for row in answers:
        keyboard.add(InlineKeyboardButton(text=row, callback_data=row))

    return word_en_id, word_en, part_of_speech, translation, keyboard.adjust(2).as_markup()


