from sqlalchemy import create_engine

from db.objects import Base

engine = create_engine("sqlite:///database.db")
Base.metadata.create_all(engine)