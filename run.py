import logging, asyncio

from aiogram import Dispatcher, Bot

from config import TOKEN
from app.handler import router


bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler('log.log'),
            logging.StreamHandler()
        ]
    )

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')