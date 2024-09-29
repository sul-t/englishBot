import sqlite3, random

from typing import Any, Callable, Dict, Awaitable
from aiogram import Router, F, BaseMiddleware
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, TelegramObject
import app.keyboard as kb


async def send_words(message, user_id):
    if cursor.execute('select user_id from users where user_id = ?', (user_id,)).fetchone() is None:
        cursor.execute('insert into users(user_id) values(?)', (user_id,))

    word_en_id, word_en, part_of_speech, translation, keyboard = await kb.generate_words()

    cursor.execute('update users set word_id = ?, word = ? where user_id = ?', (word_en_id, translation, user_id))

    await message.answer(f'Выберите перевод слова <strong><i>{word_en}</i></strong>, часть речи — <strong><i>{part_of_speech}</i></strong>', reply_markup=keyboard, parse_mode='HTML')

    connect.commit()


class GetUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ):
        user = data['event_from_user']
        data['user'] = cursor.execute('select * from users where id = ?', (user.id,)).fetchone()


router = Router()
# router.message.middleware(GetUserMiddleware())

connect = sqlite3.connect('./english.db')
cursor = connect.cursor()
# cursor.row_factory = sqlite3.Row



@router.message(CommandStart())
async def start(msg: Message):
    # num = random.randint(1, 200)
    # bilet_id = num - 1
    # cursor.execute('update users set bilet_id = ?, word_index = 0', (bilet_id,))

    # await main(msg)

    await send_words(msg, msg.from_user.id)

@router.message()
async def main(msg: Message):
    await send_words(msg, msg.from_user.id)
    print('sanya')
    # это может умереть, судя по типизации
    # bilet_id, question_index = cursor.execute('select bilet_id, question_index from users where id = ?', (msg.from_user.id)).fetchone()

    

@router.callback_query()
async def check_response(callback: CallbackQuery):
    await callback.answer()

    word_en_id = cursor.execute('select word_id from users where user_id = ?', (callback.from_user.id,)).fetchone()[0]
    word_en, part_of_sheech = cursor.execute('select word, part_of_speech from words where id = ?',(word_en_id,)).fetchone()
    word_ru = cursor.execute('select translation from translations where word_id = ?', (word_en_id,)).fetchall()

    word_list = []

    for word in word_ru:
        word_list.append(word)

    print(word_list)

    if callback.data == 'не знаю':
        await callback.message.answer(f'{word_en}, часть речи {part_of_sheech} варианты переводов: {word_list}')

    word = cursor.execute('select word from users where user_id = ?', (callback.from_user.id,)).fetchone()[0]

    if word != callback.data:
        await callback.message.answer(f'Неверно! Правильно - {word}')
    else:
        await callback.message.answer('Верно!')

    await send_words(callback.message, callback.from_user.id)


