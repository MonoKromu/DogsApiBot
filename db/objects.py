from datetime import datetime
from typing import Optional, List

from sqlalchemy import DateTime, ForeignKey, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


user_favorite_breeds = Table(
    "user_favorite_breeds",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("breed_id", ForeignKey("breed.id"), primary_key=True)
)


class Breed(Base):
    __tablename__ = "breed"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    main_image: Mapped[str]
    rus_name: Mapped[Optional[str]]


class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    favorite_breeds: Mapped[List["Breed"]] = relationship(secondary=user_favorite_breeds)


class Group(Base):
    __tablename__ = "group"
    id: Mapped[int] = mapped_column(primary_key=True)
    timer: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_posted: Mapped[Optional[datetime]] = mapped_column(DateTime)
