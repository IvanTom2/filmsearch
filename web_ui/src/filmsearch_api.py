import asyncio
from aiohttp import ClientSession


class Genre(object):
    def __init__(
        self,
        ui: str,
        url: str,
        api: str,
        prirority: int,
    ) -> None:
        self.ui = ui
        self.url = url
        self.api = api
        self.prirority = prirority

    def __eq__(self, __other: object) -> bool:
        if not isinstance(__other, self.__class__):
            raise ValueError(f"Can't compare {self.__class__} and {__other.__class__}")
        if self.prirority == __other.prirority:
            return True
        return False

    def __gt__(self, __other: object) -> bool:
        if not isinstance(__other, self.__class__):
            raise ValueError(f"Can't compare {self.__class__} and {__other.__class__}")
        if self.prirority > __other.prirority:
            return True
        return False


class Genres(object):
    THRILLER = Genre("Триллер", "thriller", "триллер", 1)
    ACTION = Genre("Боевик", "action", "боевик", 2)
    WAR = Genre("Военный", "war", "военный", 3)
    DRAMA = Genre("Драма", "drama", "драма", 4)
    FANTASY = Genre("Фэнтези", "fantasy", "фэнтези", 5)
    SCIFI = Genre("Фантастика", "scifi", "фантастика", 6)
    COMEDY = Genre("Комедия", "comedy", "комедия", 7)
    CRIME = Genre("Криминал", "crime", "криминал", 8)
    HISTORICAL = Genre("Исторический", "historical", "история", 9)
    BIOPIC = Genre("Биография", "biopic", "биография", 10)
    CARTOON = Genre("Мультфильм", "cartoon", "мультфильм", 12)
    ANIME = Genre("Аниме", "anime", "аниме", 100)
    MELODRAMA = Genre("Мелодрама", "melodrama", "мелодрама", 100)
    FAMILY = Genre("Семейный", "family", "семейный", 100)

    def __init__(self):
        self.all = self._setup()

        self.mapper = {genre.url: genre for genre in self.all}

    def map(self, url_name: str):
        return self.mapper.get(url_name, None)

    @classmethod
    def _setup(self):
        _all = [g for g in self.__dict__.values() if isinstance(g, Genre)]
        _all.sort()
        return _all

    @property
    def default(self) -> Genre:
        return self.THRILLER


class FilmSearchAPI(object):
    def __init__(
        self,
        URL: str,
    ) -> None:
        self.URL = URL

        self._session = ClientSession(self.URL)

    def create_session(self):
        if not self._session:
            self._session = ClientSession(self.URL)

    async def destroy_session(self):
        await self._session.close()

    async def get_film(self, slug: str) -> dict:
        async with self._session.get(f"/film/{slug}") as response:
            data = await response.json()
        return data

    async def films_by_genre(self, genre: str) -> dict:
        async with self._session.get(f"/genres/{genre}") as response:
            data = await response.json()
        return data

    async def text_search(self, text: str) -> dict:
        async with self._session.get(f"/text_search/{text}") as response:
            data = await response.json()
        return data


async def main():
    api = FilmSearchAPI("http://127.0.0.1:8001")
    api.create_session()

    # data = await api.get_film("forrest-gump")
    # data = await api.get_genre("комедия")
    data = await api.text_search("форрест")
    print(data)

    await api.destroy_session()


if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    g = Genres()
    print([v.ui for v in g.all])
