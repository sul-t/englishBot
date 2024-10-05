import sqlite3, random

from typing import Any, Callable, Dict, Awaitable
from aiogram import Router, F, BaseMiddleware
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, TelegramObject
import app.keyboard as kb


async def send_words(message, user_id):
    if cursor.execute('select user_id from users where user_id = ?', (user_id,)).fetchone() is None:
        cursor.execute('insert into users(user_id) values(?)', (user_id,))

    word_en_id, word_en, part_of_speech, translation, keyboard = await kb.generate_words(user_id)

    cursor.execute('update users set word_id = ?, word = ? where user_id = ?', (word_en_id, translation, user_id))

    await message.answer(f'🔍 Выберите перевод слова <strong><i>{word_en}</i></strong>. 📝 Часть речи — <strong><i>{part_of_speech}</i></strong>', reply_markup=keyboard, parse_mode='HTML')

    connect.commit()


router = Router()

connect = sqlite3.connect('./english.db')
cursor = connect.cursor()



def isdigit(text):
    try:
        return int(text)
    except ValueError:
        return None


@router.message(Command('bilet'))
async def choice_bilet(message: Message):
    await message.answer('🎟️ Выберите номер билета от 0 до 200.\n📩 Отправьте -1, чтобы учить все слова сразу!')


@router.message()
async def main(msg: Message):
    text = isdigit(msg.text)

    if (text is not None) and (-1 <= text < 200):
        await msg.answer(f'Вы решаете {text} билет')
        cursor.execute('update users set bilet = ? where user_id = ?', (text, msg.from_user.id))
        connect.commit()
    
    await send_words(msg, msg.from_user.id)


@router.callback_query()
async def check_response(callback: CallbackQuery):
    await callback.answer()

    word_en_id = cursor.execute('select word_id from users where user_id = ?', (callback.from_user.id,)).fetchone()[0]
    word_en, part_of_sheech = cursor.execute('select word, part_of_speech from words where id = ?',(word_en_id,)).fetchone()
    words_ru = cursor.execute('select translation from translations where word_id = ?', (word_en_id,)).fetchall()

    list_ru_words = ', '.join(word[0] for word in words_ru)

 
    if callback.data == 'Не знаю':
        await callback.message.answer(f'📚 Английское слово: <b>{word_en}</b>\n📝 Часть речи: <b>{part_of_sheech}</b>\n🌍 Перевод слова: <b>{list_ru_words}</b>', parse_mode='HTML')

        return await send_words(callback.message, callback.from_user.id)

    word = cursor.execute('select word from users where user_id = ?', (callback.from_user.id,)).fetchone()[0]

    if word != callback.data:
        await callback.message.answer(f'❌ Неверно!\n📚 Английское слово: <b>{word_en}</b>\n📝 Часть речи: <b>{part_of_sheech}</b>\n🌍 Перевод слова: <b>{list_ru_words}</b>', parse_mode='HTML')
    else:
        await callback.message.answer('Верно!')

    return await send_words(callback.message, callback.from_user.id)


