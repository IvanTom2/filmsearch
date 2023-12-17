import asyncio
import json
from pathlib import Path
from typing import Awaitable
from functools import wraps
from asyncio import Semaphore
from aiohttp import ClientSession
from aiolimiter import AsyncLimiter


JSON_PATH = 1
IMG_PATH = 1


class KPScraper(object):
    def __init__(
        self,
        api_key: str,
        limit_per_sec: int = 19,
        semaphore_limit: int = 3,
    ) -> None:
        self._loop = asyncio.get_running_loop()

        self._headers = self._setup_headers(api_key)
        self._session = None
        self._limit = AsyncLimiter(limit_per_sec, 1)

        self.semaphore = Semaphore(semaphore_limit)

    def limited(coro: Awaitable):
        @wraps(coro)
        async def wrapper(self, *args, **kwargs):
            self._limit: AsyncLimiter
            async with self.semaphore:
                async with self._limit:
                    output = await coro(self, *args, **kwargs)

            return output

        return wrapper

    def _setup_headers(self, api_key: str) -> dict:
        return {
            "X-API-KEY": api_key,
        }

    def _get_session(self) -> ClientSession:
        return ClientSession(
            loop=self._loop,
            headers=self._headers,
        )

    def unpack(self, data) -> dict:
        packs = {
            "genres": "genre",
            "countries": "country",
        }

        for key in packs.keys():
            if key in data:
                values = data[key]
                values = list(map(lambda x: x[packs[key]], values))
                data[key] = values

        return data

    @limited
    async def get_image(self, id: str) -> bytes:
        URL = f"https://kinopoiskapiunofficial.tech/images/posters/kp/{id}.jpg"
        async with self._get_session() as session:
            async with session.get(URL) as response:
                image = await response.read()
        return image

    @limited
    async def get_info(self, id: str) -> dict:
        URL = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{id}"
        async with self._get_session() as session:
            async with session.get(URL) as response:
                data = await response.json()

        data = self.unpack(data)
        return data


async def main():
    loop = asyncio.get_event_loop()
    parser = KPScraper(loop, "0ba6ea1c-e34f-43e3-8da5-7041b14cbbfe")

    async with parser:
        data = await parser.get_info("999")

    with open("film2.json", "w") as file:
        file.write(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
