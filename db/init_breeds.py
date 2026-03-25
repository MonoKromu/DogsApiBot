import asyncio

from sqlalchemy.orm import Session

import db.engine
import api
from db.objects import Breed


async def init_breeds():
    breeds_list = list((await api.list_all()).get("message").keys())
    tasks = [api.by_breed(breed) for breed in breeds_list]
    urls = [res.get("message") for res in await asyncio.gather(*tasks)]
    with Session(db.engine.engine) as session:
        breeds = [Breed(id=i, name=name, main_image=url) for i, name, url in
                  zip(range(1, len(breeds_list) + 1), breeds_list, urls)]
        session.add_all(breeds)
        session.commit()