import random

from aiogram import Router
from aiogram.filters import CommandObject, Command
from aiogram.types import Message, URLInputFile
from sqlalchemy.orm import Session

import api
from db import db_operations, engine

router = Router()


@router.message(Command("add_fav"))
async def add_favorite_breed(message: Message, command: CommandObject):
    with Session(engine.engine) as session:
        if not command.args:
            await message.answer("Вы не выбрали породу")
            return
        breed_name = command.args.split()[0]
        user = db_operations.get_user(message.from_user.id, session)
        breed_list = user.favorite_breeds
        new_breed = db_operations.get_breed(breed_name, session)
        if not new_breed:
            await message.answer("Такая порода не найдена")
            return
        if new_breed in breed_list:
            await message.answer("Эта порода уже есть в вашем списке")
            return

        answer = "Порода добавлена в ваш список"
        sub_breeds = new_breed.sub_breeds
        parent_breed = new_breed.parent_breed
        if not new_breed.is_sub_breed and sub_breeds and any([(breed in breed_list) for breed in sub_breeds]):
            for sub in sub_breeds:
                if sub in breed_list:
                    breed_list.remove(sub)
            answer += ". В выдаче теперь участвуют все её подвиды"
        elif new_breed.is_sub_breed and parent_breed in breed_list:
            breed_list.remove(parent_breed)
            answer += f". Теперь в выдаче участвуют только выбранные подвиды этой породы"
        breed_list.append(new_breed)

        session.commit()
        await message.answer(answer)


@router.message(Command("list_fav"))
async def list_favorite_breeds(message: Message):
    with Session(engine.engine) as session:
        user = db_operations.get_user(message.from_user.id, session)
        breed_list = user.favorite_breeds
        if not breed_list:
            await message.answer("Вы еще не добавили породы в свой список")
            return
        answer = "Список ваших избранных пород:\n - "
        answer += "\n - ".join([breed.name.capitalize() if "-" not in breed.name else
                                breed.name.split("-")[0].capitalize() + f" ({breed.name.split("-")[1]})"
                                for breed in breed_list])
        await message.answer(answer)


@router.message(Command("del_fav"))
async def del_favorite_breed(message: Message, command: CommandObject):
    with Session(engine.engine) as session:
        if not command.args:
            await message.answer("Вы не выбрали породу")
            return
        breed_name = command.args.split()[0]
        user = db_operations.get_user(message.from_user.id, session)
        breed_list = user.favorite_breeds
        if not breed_list:
            await message.answer("Ваш список пород и так пуст")
        del_breed = db_operations.get_breed(breed_name, session)
        if not del_breed:
            await message.answer("Такая порода не найдена")
            return
        if del_breed not in breed_list:
            await message.answer("Этой породы нет в вашем списке")
        breed_list.remove(del_breed)
        session.commit()
        await message.answer("Порода удалена из вашего списка")


@router.message(Command("clear_fav"))
async def clear_favorite_breeds(message: Message):
    with Session(engine.engine) as session:
        user = db_operations.get_user(message.from_user.id, session)
        breed_list = user.favorite_breeds
        if not breed_list:
            await message.answer("Ваш список пород и так пуст")
            return
        breed_list.clear()
        session.commit()
        await message.answer("Ваш список избранных пород очищен")


@router.message(Command("fav"))
async def send_image(message: Message):
    with Session(engine.engine) as session:
        user = db_operations.get_user(message.from_user.id, session)
        breed_list = user.favorite_breeds
        if not breed_list:
            await message.answer("Вы еще не добавили породы в свой список")
            return
        search_breed = breed_list[random.randint(0, len(breed_list) - 1)]
        api_response = await api.by_breed(search_breed.name.replace("-", "/"))
        if "error" in api_response:
            await message.answer(f"Произошла ошибка при отправке изображения: {api_response.get('message')}")
        else:
            url = api_response.get("message")
            image = URLInputFile(url)
            await message.answer_photo(photo=image)
