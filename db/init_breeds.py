import asyncio

from sqlalchemy.orm import Session

import api
import db.engine
from api import by_breed
from db.objects import Breed


async def init_breeds():
    with Session(db.engine.engine) as session:
        breeds = (await api.list_all()).get("message")
        base_breeds = breeds.keys()
        base_breeds_images = [res.get("message") for res in
                              await asyncio.gather(*[by_breed(breed) for breed in base_breeds])]
        db_base_breeds = [Breed(name=breed, main_image=image) for breed, image in zip(base_breeds, base_breeds_images)]
        for base_breed in db_base_breeds:
            sub_breeds = breeds.get(base_breed.name)
            if sub_breeds:
                sub_breeds_images = [res.get("message") for res in
                                     await asyncio.gather(*[by_breed(f"{base_breed}/{breed}") for breed in sub_breeds])]
                db_sub_breeds = [Breed(name=breed, main_image=image) for breed, image in
                                 zip(sub_breeds, sub_breeds_images)]
                base_breed.sub_breeds = db_sub_breeds
        session.add_all(db_base_breeds)
        session.commit()


if __name__ == "__main__":
    result = asyncio.run(init_breeds())
    print(result)
