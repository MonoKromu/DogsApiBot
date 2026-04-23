from typing import Literal, List

from sqlalchemy.orm import Session

from db.objects import Breed, User


def get_breed(name: str, session: Session):
    breed = session.query(Breed).where(Breed.name == name).first()
    return breed


def list_breeds(mode: Literal["main", "sub", "all"], session: Session):
    query = session.query(Breed)
    if mode == "main":
        query.filter(~Breed.is_sub_breed)
    elif mode == "sub":
        query.filter(Breed.is_sub_breed)
    breeds = query.all()
    return breeds


def get_user(user_id: int, session: Session):
    user = session.query(User).where(User.id == user_id).first()
    if not user:
        user = User(id=user_id)
        session.add(user)
        session.commit()
    return user
