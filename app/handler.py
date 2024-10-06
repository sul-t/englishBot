import sqlite3, random

from typing import Any, Callable, Dict, Awaitable
from aiogram import Router, F, BaseMiddleware
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, TelegramObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import app.keyboard as kb



async def send_words(message, user_id):
    if cursor.execute('select user_id from users where user_id = ?', (user_id,)).fetchone() is None:
        cursor.execute('insert into users(user_id) values(?)', (user_id,))

    word_en_id, word_en, part_of_speech, keyboard = await kb.generate_words(user_id)

    cursor.execute('update users set word_id = ? where user_id = ?', (word_en_id, user_id))

    if cursor.execute('select hard_mode from users where user_id = ?', (user_id,)).fetchone()[0]:
        await message.answer(f'🔍 Выберите перевод слова <strong><i>{word_en}</i></strong>. 📝 Часть речи — <strong><i>{part_of_speech}</i></strong>', parse_mode='HTML')
    else:
        await message.answer(f'🔍 Выберите перевод слова <strong><i>{word_en}</i></strong>. 📝 Часть речи — <strong><i>{part_of_speech}</i></strong>', reply_markup=keyboard, parse_mode='HTML')

    connect.commit()


async def processUserAnswer(text, message, user_id):
    word_en_id = cursor.execute('select word_id from users where user_id = ?', (user_id,)).fetchone()[0]
    word_en, part_of_speech = cursor.execute('select word, part_of_speech from words where id = ?',(word_en_id,)).fetchone()
    words_ru = cursor.execute('select translation from translations where word_id = ?', (word_en_id,)).fetchall()

    list_ru_words = ', '.join(word[0] for word in words_ru)

    if (text).lower() == 'не знаю':
        await message.answer(f'📚 Английское слово: <b>{word_en}</b>\n📝 Часть речи: <b>{part_of_speech}</b>\n🌍 Перевод слова: <b>{list_ru_words}</b>', parse_mode='HTML')

        return await send_words(message, user_id)

    row = cursor.execute('select translation from translations where word_id = (select word_id from users where user_id = ?)', (user_id,)).fetchall()
    
    rigth_words = [word[0] for word in row]

    if text.lower() not in rigth_words:
        await message.answer(f'❌ Неверно!\n📚 Английское слово: <b>{word_en}</b>\n📝 Часть речи: <b>{part_of_speech}</b>\n🌍 Перевод слова: <b>{list_ru_words}</b>', parse_mode='HTML')
    else:
        await message.answer('Верно!')

    return await send_words(message, user_id)


def isdigit(text):
    try:
        return int(text)
    except ValueError:
        return None



router = Router()

connect = sqlite3.connect('./english.db')
cursor = connect.cursor()



class biletDialogStates(StatesGroup):
    number_bilet = State()



@router.message(CommandStart())
async def start(message: Message):
    if cursor.execute('select user_id from users where user_id = ?', (message.from_user.id,)).fetchone() is None:
        cursor.execute('insert into users(user_id) values(?)', (message.from_user.id,))
        connect.commit()

    await message.answer('Изучай английские слова с помощью данного бота', reply_markup=kb.reply_keyboard())


@router.message(F.text == 'Билет')
async def choose_bilet(message: Message, state: FSMContext):
    await message.answer('🎟️ Отправьте число от 1 до 200, оно будет соответствовать номеру билета.\n📩 Отправьте 0, чтобы учить все слова сразу!', reply_markup=kb.reply_keyboard())
    await state.set_state(biletDialogStates.number_bilet)

@router.message(F.text, biletDialogStates.number_bilet)
async def update_chosen_bilet(message: Message, state: FSMContext):
    number_bilet = isdigit(message.text)

    if (number_bilet is not None) and (0 <= number_bilet <= 200):
        await message.answer(f'Вы решаете {number_bilet} билет')
        cursor.execute('update users set bilet = ? where user_id = ?', (number_bilet, message.from_user.id))
        connect.commit()

    await send_words(message, message.from_user.id)


@router.message(F.text == 'Режим')
async def change_mode(message: Message):
    hard_mode = cursor.execute('update users set hard_mode = not hard_mode returning hard_mode').fetchone()[0]
    connect.commit()
 
    mode = 'сложный' if hard_mode else 'простой'

    await message.answer(f'Ваш режим был изменен на {mode}!')
    await send_words(message, message.from_user.id)


@router.message()
async def main(message: Message):
    if cursor.execute('select hard_mode from users where user_id = ?', (message.from_user.id,)).fetchone()[0]:
        return await processUserAnswer(message.text, message, message.from_user.id)

    await send_words(message, message.from_user.id)


@router.callback_query()
async def check_response(callback: CallbackQuery):
    await callback.answer()

    await processUserAnswer(callback.data, callback.message, callback.from_user.id)

 
    


