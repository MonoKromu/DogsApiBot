import asyncio
import aiohttp
import json
from api_key import key
from telegram import Update
from telegram.ext import (ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, MessageHandler,
                          Application, filters)


breeds = {}
breeds_str = ""
current_breed = "breeds/image"


async def fetch_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()


async def launch(app: Application):
    global breeds
    global breeds_str
    url = "https://dog.ceo/api/breeds/list/all"
    data = await fetch_data(url)
    breeds = json.loads(data)["message"]
    print(type(breeds))
    breeds_str = "\n".join([f"{breed}, {f"({", ".join(sub)})" if len(sub) > 0 else ""}" for breed, sub in breeds.items()])


async def breeds_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global breeds_str
    await context.bot.send_message(chat_id=update.effective_chat.id, text=breeds_str)


async def random_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_breed
    url = f"https://dog.ceo/api/{current_breed}/random"
    data = await fetch_data(url)
    image_url = json.loads(data)["message"]
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)


async def set_breed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter breed name:")
    return BREED


async def set_breed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_breed
    breed = update.message.text
    context.user_data["breed"] = breed
    if breed in list(breeds.keys()):
        if len(breeds[breed]) == 0:
            current_breed = f"breed/{breed}/images"
            await update.message.reply_text(f"Breed was successfully set: {breed}")
            return ConversationHandler.END
        else:
            await update.message.reply_text("Enter sub breed:")
            return SUB_BREED
    else:
        await update.message.reply_text("No such breed. Try again")
        return ConversationHandler.END


async def set_sub_breed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_breed
    breed = context.user_data["breed"]
    sub_breed = update.message.text
    if sub_breed in breeds[breed]:
        current_breed = f"breed/{breed}/{sub_breed}/images"
        await update.message.reply_text(f"Breed was successfully set: {sub_breed} {breed}")
        return ConversationHandler.END
    else:
        await update.message.reply_text(f"No such sub breed. Breed was set: {breed}")
        return ConversationHandler.END


application = ApplicationBuilder().token(key).post_init(launch).build()
breeds_handler = CommandHandler("breeds", breeds_command)
random_handler = CommandHandler("random", random_command)
BREED, SUB_BREED = range(2)
set_breed_handler = ConversationHandler(entry_points=[CommandHandler("set_breed", set_breed_command)],
                                        states = {
                                            BREED: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_breed)],
                                            SUB_BREED: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_sub_breed)],
                                        },
                                        fallbacks=[breeds_handler])
application.add_handler(breeds_handler)
application.add_handler(random_handler)
application.add_handler(set_breed_handler)

application.run_polling()