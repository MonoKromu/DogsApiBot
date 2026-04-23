import sys

from sqlalchemy import create_engine

from db.objects import Base

engine = create_engine("sqlite:///database.db", echo=("debug" if "--debug" in sys.argv else False))
Base.metadata.create_all(engine)