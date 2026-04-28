from aiogram import Router, html
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

router = Router()

commands_short = {
    "/random": "Получить абсолютно случайную картинку",
    "/list": "Просмотреть список всех пород",
    "/fav": "Получить картинку собаки из вашего списка пород",
    "/info": "Вывести полный список команд с подробным описанием"
}

commands_full = {
    "/random": "Выбрать случайную породу из списка всех пород и получить случайную картинку собаки этой породы",
    "/list": "Вывести интерактивный список всех доступных пород. (Активным остается только последний выведенный список)",
    "/page {номер}": "Перелистнуть последний выведенный список сразу на конкретную страницу",
    "/fav": "Выбрать случайную породу из вашего избранного списка и получить случайную картинку собаки этой породы",
    "/add_fav {порода}": "Добавить породу в ваш список избранного. Название должно быть из списка пород маленькими буквами. "
                         "Для подвидов: {порода-подвид}",
    "/del_fav {порода}": "Удалить породу из вашего списка избранного. Требования к формату те же, что и при добавлении",
    "/clear_fav": "Очистить ваш список пород",
    "/info": "Вывести эту справку"
}

commands_full_short = {
    "/random": "Получить случайную картинку собаки",
    "/list": "Вывести список всех пород",
    "/page": "Перелистнуть список на конкретную страницу",
    "/fav": "Получить случайную картинку собаки из вашего списка пород",
    "/add_fav": "Добавить породу в ваш список избранного",
    "/del_fav": "Удалить породу из вашего списка избранного",
    "/clear_fav": "Очистить ваш список пород",
    "/info": "Вывести эту справку"
}


@router.message(CommandStart())
async def start(message: Message):
    commands_list_text = "\n".join([f" • {k} - {v}" for k, v in commands_short.items()])

    buttons = [[KeyboardButton(text="/random"), KeyboardButton(text="/fav")],
               [KeyboardButton(text="/list")]]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    text = (html.bold("Привет! ") + "Я бот, который может отправлять тебе картинки собачек.\n" +
            "Вот мои основные команды:\n" +
            commands_list_text + "\n")
    await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)


@router.message(Command("info"))
async def info(message: Message):
    commands_list_text = "\n".join([f" • {k} - {v}" for k, v in commands_full.items()])
    text = (html.bold("Полный список команд:") + "\n" + commands_list_text)
    await message.answer(text, parse_mode=ParseMode.HTML)
