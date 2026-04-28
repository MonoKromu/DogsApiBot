import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.types import Message, URLInputFile, BotCommand, BotCommandScopeDefault

import api
from config import config
from db.init_breeds import init_breeds
from routers import favorite_breeds, list_breeds, info

bot = Bot(config.bot_token.get_secret_value())
dp = Dispatcher(events_isolation=SimpleEventIsolation())


@dp.message(Command("random"))
async def random(message: Message):
    api_response = await api.random()
    if "error" in api_response:
        await message.answer(f"Произошла ошибка при отправке изображения: {api_response.get('message')}")
    else:
        url = api_response.get("message")
        image = URLInputFile(url)
        await message.answer_photo(photo=image)


async def set_commands():
    bot_commands = [BotCommand(command=k, description=v) for k, v in info.commands_full_short.items()]
    await bot.set_my_commands(bot_commands, scope=BotCommandScopeDefault())


async def main():
    await set_commands()
    dp.include_router(info.router)
    dp.include_router(favorite_breeds.router)
    dp.include_router(list_breeds.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    if "--reinit" in sys.argv:
        asyncio.run(init_breeds())
    asyncio.run(main())
