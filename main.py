from os import getenv
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from handlers.routes import router

load_dotenv()
TOKEN = getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError(
        "Не найден BOT_TOKEN! Проверьте файл .env"
    )

dp = Dispatcher()
dp.include_router(router)

async def main():
    bot = Bot(token=TOKEN)

    print("Start..")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
