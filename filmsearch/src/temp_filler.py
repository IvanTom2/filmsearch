import sys
import asyncio
import aiofiles
import json
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent.parent))
from db import DataBaseInterface, load_config
from scrapers.kinopoisk import KPScraper


class Filler(object):
    def __init__(
        self,
        path: Path,
        config: dict[str],
        db_conn: int = 6,
    ):
        self.dbi = DataBaseInterface(config, db_conn)

        self.img_path = path / "images"
        self.json_path = path / "jsons"

    async def save_img(self, data: bytes, path: Path) -> None:
        async with aiofiles.open(str(path), mode="wb") as file:
            await file.write(data)
        return str(path)

    async def save_json(self, data: dict, path: Path) -> None:
        async with aiofiles.open(str(path), mode="w") as file:
            await file.write(json.dumps(data, ensure_ascii=False))
        return str(path)

    async def task(self, scraper: KPScraper, film_id):
        json_data = await scraper.scrape_info(film_id)
        image = await scraper.get_image(film_id)

        await self.save_json(json_data, self.json_path / f"{film_id}.json")
        img_path = await self.save_img(image, self.img_path / f"{film_id}.jpg")

        id = await self.dbi.insert_film(json_data)
        await self.dbi.insert_film_poster(id, img_path)

    async def main(self, loop: asyncio.AbstractEventLoop):
        await self.dbi.create_pool()

        films_ids = [435, 326, 535341, 448, 258687, 3498, 329, 370, 361, 342]
        films_ids = list(map(lambda x: str(x), films_ids))

        scraper = KPScraper(loop, "0ba6ea1c-e34f-43e3-8da5-7041b14cbbfe")
        tasks = [
            asyncio.create_task(self.task(scraper, film_id)) for film_id in films_ids
        ]

        await asyncio.gather(*tasks)
        await self.dbi.destroy_pool()

    def fill(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main(loop))


if __name__ == "__main__":
    config = load_config()
    path = Path(__file__).parent.parent / "data"

    filler = Filler(path, config)

    filler.fill()
