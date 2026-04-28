from typing import Literal, List

from sqlalchemy.orm import Session

from db.objects import Breed, User


def get_breed(name: str, session: Session):
    breed = session.query(Breed).where(Breed.name == name).first()
    return breed


def list_breeds(mode: Literal["main", "sub", "all"], session: Session, page=None, main_name=None):
    query = session.query(Breed)
    if mode == "main":
        query = query.filter(~Breed.is_sub_breed)
    elif mode == "sub":
        query = query.filter(Breed.is_sub_breed)
        if main_name:
            query.filter(Breed.parent_breed.has(name=main_name))

    if page:
        page -= 1
        query = query.offset(max(0, page * 10 - 1))
        query = query.limit(10)

    breeds = query.all()
    return breeds


def get_user(user_id: int, session: Session):
    user = session.query(User).where(User.id == user_id).first()
    if not user:
        user = User(id=user_id)
        session.add(user)
        session.commit()
    return user
