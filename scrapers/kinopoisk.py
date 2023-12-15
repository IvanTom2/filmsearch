import asyncio
import json
from pathlib import Path
from typing import Awaitable, Optional, Type
from types import TracebackType
from functools import wraps
from asyncio import AbstractEventLoop
from aiohttp import ClientSession
from aiolimiter import AsyncLimiter


class KPScraper(object):
    def __init__(
        self,
        loop: AbstractEventLoop,
        api_key: str,
        limit_per_sec: int = 19,
    ) -> None:
        self._loop = loop

        self._headers = self._setup_headers(api_key)
        self._session = None
        self._limit = AsyncLimiter(limit_per_sec, 1)

    def limited(coro: Awaitable):
        @wraps(coro)
        async def wrapper(self, *args, **kwargs):
            self._limit: AsyncLimiter
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
            headers=self._headres,
        )

    @limited
    async def get_image(self, id: str) -> None:
        PATH = Path(__file__).parent.parent / "data" / "posters"
        URL = f"https://kinopoiskapiunofficial.tech/images/posters/kp/{id}.jpg"
        async with self._session.get(URL) as response:
            image = await response.read()

        with open(PATH / "301.jpg", "wb") as file:
            file.write(image)

    @limited
    async def scrape_info(self, id: str):
        URL = f"https://kinopoiskapiunofficial.tech/api/v2.2/films/{id}"
        async with self._session.get(URL) as response:
            data = await response.json()

        return data

    async def __aenter__(self):
        self._session = ClientSession(
            headers=self._headers,
            loop=self._loop,
        )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ):
        await self._session.close()


async def main():
    loop = asyncio.get_event_loop()
    parser = KPScraper(loop, "0ba6ea1c-e34f-43e3-8da5-7041b14cbbfe")

    async with parser:
        data = await parser.scrape_info("301")

    # print(data)


if __name__ == "__main__":
    asyncio.run(main())
