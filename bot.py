import aiohttp
import json
import datetime
from api_key import key
from telegram import Update, BotCommand, ReplyKeyboardMarkup
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler,
                          Application, filters)
from bs4 import BeautifulSoup
from functools import wraps


breeds = {}
breeds_str = ""
default_breed = "breeds/image"


def logger(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        write_log(update.effective_chat.id, update.message.text, update.effective_user.full_name)
        result = await func(update, context)
        reply = context.user_data[f"{chat_id}_bot_reply"]
        write_log(update.effective_chat.id, reply, "Dogs pictures")
        return result
    return wrapper


def write_log(user_id, text, sender):
    with open(f"logs/{str(user_id)}.txt", "a", encoding="utf-8") as file:
        file.write(f" - {datetime.datetime.now()} - {sender}:\n{text}\n")


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        response = await session.get(url)
        return await response.text()


async def launch(app: Application):
    global breeds
    global breeds_str
    url = "https://dog.ceo/api/breeds/list/all"
    data = await fetch_data(url)
    breeds = json.loads(data)["message"]
    print(type(breeds))
    breeds_str = "\n".join([f"{breed} {f"({", ".join(sub)})" if len(sub) > 0 else ""}"
                            for breed, sub in breeds.items()])


@logger
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = [
        BotCommand("start", "Show bot info"),
        BotCommand("breeds", "Show list of all available breeds"),
        BotCommand("random", "Show random picture of dog of a set breed"),
        BotCommand("set_breed", "Set breed of dogs"),
        BotCommand("reset_breed", "Reset breed to default")
    ]
    await context.bot.set_my_commands(commands)
    keyboard = [["/random"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    url = "https://dog.ceo/dog-api/"
    data = await fetch_data(url)
    http = BeautifulSoup(data, features="html.parser")
    title = http.find("h1", {"class": "title"}).get_text()
    reply = await update.message.reply_text(f"{title}\nUse commands to get pictures of dogs", reply_markup=reply_markup)
    context.user_data[f"{update.effective_chat.id}_bot_reply"] = reply.text


@logger
async def breeds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global breeds_str
    reply = await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Breeds list:\n{breeds_str}")
    context.user_data[f"{update.effective_chat.id}_bot_reply"] = reply.text


@logger
async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    url = f"https://dog.ceo/api/{context.user_data.get(f"{chat_id}_current_breed", default_breed)}/random"
    data = await fetch_data(url)
    image_url = json.loads(data)["message"]
    reply = str(await context.bot.send_photo(chat_id=chat_id, photo=image_url))
    context.user_data[f"{chat_id}_bot_reply"] = image_url


@logger
async def set_breed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    reply_markup = ReplyKeyboardMarkup([["/cancel"]], resize_keyboard=True)
    reply = await update.message.reply_text("Enter breed name:", reply_markup=reply_markup)
    context.user_data[f"{chat_id}_bot_reply"] = reply.text
    return BREED


@logger
async def set_breed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    breed = update.message.text
    context.user_data[f"{chat_id}_breed"] = breed
    if breed in list(breeds.keys()):
        if len(breeds[breed]) == 0:
            context.user_data[f"{chat_id}_current_breed"] = f"breed/{breed}/images"
            reply = await update.message.reply_text(f"Breed was successfully set: {breed}")
            context.user_data[f"{chat_id}_bot_reply"] = reply.text
            return ConversationHandler.END
        else:
            reply = await update.message.reply_text("Enter subbreed:")
            context.user_data[f"{chat_id}_bot_reply"] = reply.text
            return SUBBREED
    else:
        reply = await update.message.reply_text("No such breed. Try again")
        context.user_data[f"{chat_id}_bot_reply"] = reply.text
        return AGAIN


@logger
async def set_subbreed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    breed = context.user_data[f"{chat_id}_breed"]
    sub_breed = update.message.text
    if sub_breed in breeds[breed]:
        context.user_data[f"{chat_id}_current_breed"] = f"breed/{breed}/{sub_breed}/images"
        reply = await update.message.reply_text(f"Breed was successfully set:  {sub_breed} {breed}")
        context.user_data[f"{chat_id}_bot_reply"] = reply.text
        return ConversationHandler.END
    else:
        reply = await update.message.reply_text(f"No such subbreed. Breed was set: {breed}")
        context.user_data[f"{chat_id}_bot_reply"] = reply.text
        return ConversationHandler.END


@logger
async def reset_breed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    context.user_data[f"{chat_id}_current_breed"] = default_breed
    reply = await update.message.reply_text("Breed was reset")
    context.user_data[f"{chat_id}_bot_reply"] = reply.text


@logger
async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    reply_markup = ReplyKeyboardMarkup([["/random"]], resize_keyboard=True)
    reply = await update.message.reply_text("Setting was cancelled", reply_markup=reply_markup)
    context.user_data[f"{chat_id}_bot_reply"] = reply.text


application = ApplicationBuilder().token(key).post_init(launch).build()
start_handler = CommandHandler("start", start_command)
breeds_handler = CommandHandler("breeds", breeds_command)
random_handler = CommandHandler("random", random_command)
BREED, SUBBREED, AGAIN = range(3)
set_breed_handler = ConversationHandler(entry_points=[CommandHandler("set_breed", set_breed_command)],
                                        states = {
                                            BREED: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_breed)],
                                            SUBBREED: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_subbreed)],
                                            AGAIN: [CommandHandler("set_breed", set_breed_command)]
                                        },
                                        fallbacks=[CommandHandler("cancel", cancel_command)])
reset_breed_handler = CommandHandler("reset_breed", reset_breed_command)
application.add_handler(start_handler)
application.add_handler(breeds_handler)
application.add_handler(random_handler)
application.add_handler(set_breed_handler)
application.add_handler(reset_breed_handler)

application.run_polling()