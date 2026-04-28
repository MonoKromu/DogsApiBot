import asyncio
from dataclasses import dataclass
from typing import List

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from sqlalchemy.orm import Session

from db import db_operations
from db.engine import engine
from db.objects import Breed

router = Router()

user_list_states = {}


@dataclass
class State:
    media: List[Message]
    list_message: Message
    page: int
    total_pages: int


class ListCallback(CallbackData, prefix="list"):
    action: int
    media_group_id: str


def generate_list_text(breed_list: List[Breed], page, total):
    list_text = f"Страница {page} из {total}\nПороды: \n"
    list_text += "".join([f" - {breed.name.capitalize()}\n" for breed in breed_list])
    return list_text


@router.message(Command("list"))
async def list_breeds(message: Message):
    with Session(engine.engine) as session:
        breed_list = db_operations.list_breeds("main", session, page=1)
        media_group = MediaGroupBuilder()
        for breed in breed_list:
            media_group.add_photo(media=breed.main_image, caption=breed.name.capitalize())
        total_pages = len(db_operations.list_breeds("main", session)) // 10 + 1
        media = await message.answer_media_group(media=media_group.build())

        list_text = generate_list_text(breed_list, 1, total_pages)
        inline_keyboard = InlineKeyboardBuilder()
        inline_keyboard.button(text="<<<",
                               callback_data=ListCallback(action=-1, media_group_id=media[0].media_group_id))
        inline_keyboard.button(text=">>>", callback_data=ListCallback(action=1, media_group_id=media[0].media_group_id))
        inline_keyboard.adjust(2)
        list_message = await message.answer(text=list_text, reply_markup=inline_keyboard.as_markup())

        user_list_states[message.from_user.id] = State(media, list_message, 1, total_pages)


async def edit_list_data(session, state, message, new_page, user_id):
    tasks = []
    breed_list = db_operations.list_breeds(mode="main", page=new_page, session=session)
    for msg, breed in zip(state.media, breed_list + [""] * (10 - len(breed_list))):
        if breed:
            name = breed.name.capitalize()
            image = breed.main_image
        else:
            name = "placeholder"
            image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBXfpEQwYVaqC3dPt0FOy1i5d5ODkko4yeXg&s"
        tasks.append(msg.bot.edit_message_media(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            media=InputMediaPhoto(media=image, caption=name)
        ))

    list_text = generate_list_text(breed_list, new_page, state.total_pages)
    tasks.append(message.bot.edit_message_text(
        chat_id=state.list_message.chat.id,
        message_id=state.list_message.message_id,
        text=list_text,
        reply_markup=state.list_message.reply_markup
    ))

    await asyncio.gather(*tasks, return_exceptions=True)
    user_list_states[user_id].page = new_page



@router.callback_query(ListCallback.filter())
async def turn_page(callback: CallbackQuery, callback_data: ListCallback):
    with Session(engine.engine) as session:
        user_id = callback.from_user.id
        state = user_list_states.get(user_id)
        if not state:
            await callback.answer(text="Произошла ошибка, попробуйте заново отправить /list", show_alert=True)
            return
        if state.media[0].media_group_id != callback_data.media_group_id:
            await callback.answer(text="Эта кнопка больше не активна", show_alert=True)
            return
        new_page = state.page + callback_data.action
        if new_page < 0 or new_page > state.total_pages:
            await callback.answer()
            return

        try:
            await edit_list_data(session, state, callback, new_page, user_id)
        except:
            pass
        await callback.answer()


@router.message(Command("page"))
async def change_page(message: Message, command: CommandObject):
    with Session(engine.engine) as session:
        user_id = message.from_user.id
        state = user_list_states.get(user_id)
        if not state:
            await message.answer("В этом диалоге нет активного списка пород. Используйте /list, чтобы посмотреть его")
            return
        args = command.args
        if not args or not args.isnumeric():
            await message.answer("Для использования команды введите номер страницы")
            return
        new_page = int(args)
        if new_page < 0 or new_page > state.total_pages:
            await message.answer("Страницы с таким номером нет")
            return
        if new_page == state.page:
            await message.answer("Вы и так находитесь на этой странице")
            return
        try:
            await edit_list_data(session, state, message, new_page, user_id)
        except:
            pass
        await message.delete()