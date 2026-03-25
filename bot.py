import asyncio
import sys

from aiogram import Bot, Dispatcher, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, URLInputFile, KeyboardButton, ReplyKeyboardMarkup

from config import config

import api
from db.init_breeds import init_breeds

bot = Bot(config.bot_token.get_secret_value())
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    commands = {
        "/random": "Получить абсолютно случайную картинку",
        "/fav": "Получить картинку собаки из вашего списка пород"
    }
    buttons = [[KeyboardButton(text=text) for text in commands.keys()]]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    commands_list_text = "\n".join([f" • {k} - {v}" for k, v in commands.items()])

    text = (html.bold("Привет! ") + "Я бот, который может отправлять тебе картинки собачек.\n" +
            "Вот мои основные команды:\n" +
            commands_list_text + "\n")
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@dp.message(Command("random"))
async def random(message: Message):
    api_response = await api.random()
    if "error" in api_response:
        await message.answer(f"Произошла ошибка при отправке изображения: {api_response.get('message')}")
    else:
        url = api_response.get("message")
        image = URLInputFile(url)
        await message.answer_photo(photo=image)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    if "--reinit" in sys.argv:
        asyncio.run(init_breeds())
    asyncio.run(main())
