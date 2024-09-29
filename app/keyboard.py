import sqlite3, random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


connect = sqlite3.connect('./english.db')
cursor = connect.cursor()


async def generate_words():
    random_list = []

    keyboard = InlineKeyboardBuilder()

    random_word = random.randint(0, 10000)
    random_list.append(random_word)

    word_en, word_en_id = cursor.execute('select word, id from words where id = ?', (random_word,)).fetchone()
    part_of_speech = cursor.execute('select part_of_speech from words where id = ?', (random_word,)).fetchone()[0]
    translations = cursor.execute('select translation from translations where word_id = ?', (random_word,)).fetchall()[0]
    translation = translations[random.randint(0, len(translations) - 1)]

    list = []

    for i in range(4):
        words_ru = cursor.execute('select translation from translations where word_id = ?', (random_word,)).fetchall()[0]
        word_ru = words_ru[random.randint(0, len(words_ru) - 1)]

        list.append(word_ru)

        while True:
            random_word = random.randint(0, 10000)

            if random_word in random_list:
                continue
            else:
                break

    random.shuffle(list)

    list.append('не знаю')

    for row in list:
        keyboard.add(InlineKeyboardButton(text=row, callback_data=row))

    return word_en_id, word_en, part_of_speech, translation, keyboard.adjust(1).as_markup()


