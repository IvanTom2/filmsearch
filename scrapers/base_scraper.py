import asyncio
import time
from aiolimiter import AsyncLimiter
from typing import Awaitable
from functools import wraps


async def end_point1():
    data = "endpoint1"
    await asyncio.sleep(0.5)
    return data


async def end_point2():
    data = "endpoint2"
    await asyncio.sleep(0.3)
    return data


async def end_point3():
    data = "endpoint3"
    await asyncio.sleep(0.2)
    return data


class BaseScraper(object):
    def __init__(self) -> None:
        self.limit = AsyncLimiter(50, 1)

    def limiter(coro: Awaitable):
        @wraps(coro)
        async def wrapper(self, *args, **kwargs):
            self.limit: AsyncLimiter
            async with self.limit:
                output = await coro(self, *args, **kwargs)
            return output

        return wrapper

    @limiter
    async def req1(self, url: str):
        data1 = await end_point1()
        data2 = await self.req2()
        data3 = await self.req3()

        return data1, data2, data3

    @limiter
    async def req2(self):
        data = await end_point2()
        return data

    @limiter
    async def req3(self):
        data = await end_point3()
        return data

    async def scrape(self, urls: str):
        tasks = [asyncio.create_task(self.req1(url)) for url in urls]
        data = await asyncio.gather(*tasks)

        return data


async def main():
    scraper = BaseScraper()

    start = time.time()
    urls = [f"url{i}" for i in range(50)]
    data = await scraper.scrape(urls)

    print("Execution time: ", time.time() - start)


if __name__ == "__main__":
    asyncio.run(main())
