import asyncio
from functools import wraps

from aiohttp import ClientSession

def retry(atts: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for i in range(atts):
                try:
                    return await func(*args, **kwargs)
                except asyncio.TimeoutError:
                    if i == atts - 1:
                        return {"status": "error", "message": "Timeout"}
                    await asyncio.sleep(2 ** i)
                except Exception as e:
                    return {"status": "error", "message": f"Something bad happened ({str(e)})"}
        return wrapper
    return decorator

@retry(5)
async def random():
    url = "https://dog.ceo/api/breeds/image/random"
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@retry(5)
async def list_all():
    url = "https://dog.ceo/api/breeds/list/all"
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

@retry(5)
async def by_breed(breed: str):
    url = f"https://dog.ceo/api/breed/{breed}/images/random"
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()