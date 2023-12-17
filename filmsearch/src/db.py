import sys
import json
import asyncio
import asyncpg
from pathlib import Path
from asyncio import Lock
from asyncpg import Pool, Connection
from abc import abstractmethod
from slugify import slugify

sys.path.append(str(Path(__file__).parent))
from models import Model, Film, FilmData, FilmStat, FilmPoster, FilmGenre, FilmCountry


DB_KEY = "database"


def load_config(root_path: Path = Path(__file__).parent.parent):
    with open(root_path / "config.json") as file:
        return json.load(file)


class DataBaseInitialize(object):
    def __init__(self, config: dict[str]) -> None:
        self.lock = Lock()

        self.DB_NAME = config["DB_NAME"]
        self.DB_HOST = config["DB_HOST"]
        self.DB_PORT = config["DB_PORT"]

        self.DB_POSTGRES = config["DB_POSTGRES"]
        self.DB_POSTGRES_PASSWORD = config["DB_POSTGRES_PASSWORD"]

        self.DB_USERNAME = config["DB_USERNAME"]
        self.DB_PASSWORD = config["DB_PASSWORD"]

    async def __creator_conn(self) -> Connection:
        connection: Connection = await asyncpg.connect(
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_POSTGRES,
            password=self.DB_POSTGRES_PASSWORD,
            database=self.DB_POSTGRES,
        )
        return connection

    async def __create_database(
        self,
        connection: Connection,
    ) -> None:
        async with self.lock:
            exists = await connection.fetch(
                f"""SELECT 1 FROM pg_catalog.pg_database
                    WHERE datname = '{self.DB_NAME}'"""
            )

            if not exists:
                await connection.execute(f"CREATE DATABASE {self.DB_NAME};")

        await self.__alter_db_owner(connection)

    async def __alter_db_owner(
        self,
        connection: Connection,
    ) -> None:
        async with self.lock:
            query = f"ALTER DATABASE {self.DB_NAME} OWNER TO {self.DB_USERNAME};"
            await connection.execute(query)

    async def _database_initiation(self) -> None:
        try:
            creator_conn = await self.__creator_conn()
            await self.__create_database(creator_conn)
            await creator_conn.close()

        finally:
            if creator_conn:
                await creator_conn.close()

    async def _user_conn(self) -> Connection:
        connection: Connection = await asyncpg.connect(
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            database=self.DB_NAME,
        )

        return connection

    async def create_new_table(
        self,
        connection: Connection,
        creation_query: str,
    ) -> None:
        async with self.lock:
            await connection.execute(
                creation_query,
            )

    @abstractmethod
    async def init_tables(self):
        try:
            await self._database_initiation()
            connection = await self._user_conn()

            self.create_new_table(connection, "query1")
            self.create_new_table(connection, "query2")
            self.create_new_table(connection, "query3")

        finally:
            if connection:
                await connection.close()


class FilmSearchDBInit(DataBaseInitialize):
    def __init__(self, DB_NAME) -> None:
        super().__init__(DB_NAME)

        self.film = Film()
        self.film_stat = FilmStat()
        self.film_data = FilmData()
        self.film_poster = FilmPoster()
        self.film_genre = FilmGenre()
        self.film_country = FilmCountry()

    async def create_film_relation(
        self,
        connection: Connection,
    ) -> None:
        query = f"""
                CREATE TABLE {self.film.TABLE_NAME} (
                {self.film.ID.db},
                {self.film.KP_ID.db} UNIQUE,
                {self.film.IMDB_ID.db} UNIQUE,
                {self.film.NAME_RU.db} NOT NULL,
                {self.film.NAME_ENG.db},
                {self.film.NAME_ORIGINAL.db},
                {self.film.YEAR.db} NOT NULL,
                {self.film.TYPE.db} NOT NULL,
                {self.film.LENGTH.db} NOT NULL,
                {self.film.SLUG.db} UNIQUE,
                {self.film.MPAA.db},
                {self.film.AGE_LIMIT.db},
                {self.film.TEXT_SEARCH_RU.db},
                PRIMARY KEY ({self.film.ID.name})
                );
                """
        print(query)
        await self.create_new_table(connection, query)

    async def create_film_stat_relation(
        self,
        connection: Connection,
    ) -> None:
        query = f"""
                CREATE TABLE {self.film_stat.TABLE_NAME} (
                {self.film_stat.ID.db} UNIQUE,
                {self.film_stat.KP_REVIEWS_COUNT.db},
                {self.film_stat.KP_GOOD_REVIEWS_COUNT.db},
                {self.film_stat.KP_REVIEWS_RATE.db},
                {self.film_stat.KP_RATE.db},
                {self.film_stat.IMDB_RATE.db},
                {self.film_stat.WORLD_CRITICS_RATE.db},
                {self.film_stat.RF_CRITICS_RATE.db},
                {self.film_stat.KP_VOTES.db},
                {self.film_stat.IMDB_VOTES.db},
                {self.film_stat.WORLD_CRITICS_VOTES.db},
                {self.film_stat.RF_CRITICS_VOTES.db},
                FOREIGN KEY ({self.film_stat.ID.name})
                    REFERENCES {self.film.TABLE_NAME}({self.film.ID.name})
                );
                """
        print(query)
        await self.create_new_table(connection, query)

    async def create_film_data_relation(
        self,
        connection: Connection,
    ) -> None:
        query = f"""
                CREATE TABLE {self.film_data.TABLE_NAME} (
                {self.film_data.ID.db} UNIQUE,
                {self.film_data.SLOGAN.db},
                {self.film_data.DESCRIPTION.db},
                {self.film_data.SHORT_DESCROPTION.db},
                FOREIGN KEY ({self.film_data.ID.name})
                    REFERENCES {self.film.TABLE_NAME}({self.film.ID.name})
                );
                """
        print(query)
        await self.create_new_table(connection, query)

    async def create_film_poster_relation(
        self,
        connection: Connection,
    ) -> None:
        query = f"""
                CREATE TABLE {self.film_poster.TABLE_NAME} (
                {self.film_poster.ID.db},
                {self.film_poster.IMAGE_PATH.db},
                FOREIGN KEY ({self.film_poster.ID.name})
                    REFERENCES {self.film.TABLE_NAME}({self.film.ID.name})
                );
                """
        print(query)
        await self.create_new_table(connection, query)

    async def create_film_genre_relation(
        self,
        connection: Connection,
    ) -> None:
        query = f"""
                CREATE TABLE {self.film_genre.TABLE_NAME} (
                {self.film_genre.ID.db},
                {self.film_genre.GENRE.db},
                FOREIGN KEY ({self.film_genre.ID.name})
                    REFERENCES {self.film.TABLE_NAME}({self.film.ID.name})
                );
                """
        print(query)
        await self.create_new_table(connection, query)

    async def create_film_country_relation(
        self,
        connection: Connection,
    ) -> None:
        query = f"""
                CREATE TABLE {self.film_country.TABLE_NAME} (
                {self.film_country.ID.db},
                {self.film_country.COUNTRY.db},
                FOREIGN KEY ({self.film_country.ID.name})
                    REFERENCES {self.film.TABLE_NAME}({self.film.ID.name})
                );
                """
        print(query)
        await self.create_new_table(connection, query)

    async def init_tables(self) -> None:
        try:
            await self._database_initiation()

            connection = await self._user_conn()
            await self.create_film_relation(connection)
            await self.create_film_stat_relation(connection)
            await self.create_film_data_relation(connection)
            await self.create_film_poster_relation(connection)
            await self.create_film_genre_relation(connection)
            await self.create_film_country_relation(connection)

        finally:
            if not connection.is_closed():
                await connection.close()


class Query(object):
    def __init__(self) -> None:
        self.model = Film()

    def insert_allocate(
        self,
        model: Model,
        json_data: dict,
        **extra_attrs,
    ) -> dict:
        data = {
            attr.name: (json_data.get(attr.api))
            for attr in model.attributes
            if json_data.get(attr.api) is not None
        }
        data.update(extra_attrs)

        attributes = "(" + ",".join(list(data.keys())) + ")"
        values = list(data.values())
        qargs = "(" + ",".join(map(lambda x: f"${x}", range(1, len(values) + 1))) + ")"

        return attributes, values, qargs

    def make_insertq(
        self,
        model: Model,
        json_data: dict,
        return_value: str | None = None,
        extra_attrs: dict = {},
    ):
        attrs, vals, qargs = self.insert_allocate(model, json_data, **extra_attrs)
        query = f"INSERT INTO {model.TABLE_NAME} {attrs} VALUES {qargs}"
        if return_value is not None:
            query += f" RETURNING {return_value}"

        return query, vals

    def make_slug(self, json_data: dict) -> str:
        text = json_data.get(self.model.NAME_ENG.api, None)
        if text is None:
            text = json_data.get(self.model.NAME_ORIGINAL.api, None)

            # need to translate ru to eng in case if no foreign names
            # if text is None:
            #     text = json_data.get(self.model.NAME_RU.api, None)

            if text is None:
                raise ValueError("Film doesn't have a name")

        slug = slugify(text)
        return slug


class DataBaseInterface(object):
    def __init__(
        self,
        config: dict[str],
        db_connections_count: int,
    ) -> None:
        self.db_connections_count = db_connections_count
        self._pool = None

        self.DB_NAME = config["DB_NAME"]
        self.DB_HOST = config["DB_HOST"]
        self.DB_PORT = config["DB_PORT"]

        self.DB_USERNAME = config["DB_USERNAME"]
        self.DB_PASSWORD = config["DB_PASSWORD"]

        self.query = Query()

        self.film = Film()
        self.film_stat = FilmStat()
        self.film_data = FilmData()
        self.film_poster = FilmPoster()
        self.film_genre = FilmGenre()
        self.film_country = FilmCountry()

    async def create_pool(self) -> None:
        print("CREATE DB CONNECTIONS POOL")
        self._pool: Pool = await asyncpg.create_pool(
            host=self.DB_HOST,
            port=self.DB_PORT,
            user=self.DB_USERNAME,
            password=self.DB_PASSWORD,
            database=self.DB_NAME,
            min_size=self.db_connections_count,
            max_size=self.db_connections_count,
        )

    async def destroy_pool(self) -> None:
        await self._pool.close()

    async def check_slug(self, slug: str) -> bool:
        async with self._pool.acquire() as connection:
            connection: Connection
            query = f"""
                    SELECT EXISTS 
                        (SELECT 1 FROM {self.film.TABLE_NAME} 
                            WHERE {self.film.SLUG.name} = $1);"""
            exists = await connection.fetchval(query, slug)

        return exists

    async def create_slug(self, json_data: dict) -> str:
        slug = self.query.make_slug(json_data)
        slug_exists = await self.check_slug(slug)
        if slug_exists:
            year = json_data.get(self.film.YEAR.api, None)
            if year is None:
                raise ValueError("Can't create slug: slug exists and year doesn't")
            slug += f"-{year}"

        return slug

    async def _execute(self, query: str, *args) -> None:
        async with self._pool.acquire() as connection:
            connection: Connection
            await connection.execute(query, *args)

    async def insert_genres(
        self,
        json_data: dict,
        id: int,
    ) -> None:
        genres = json_data.get(self.film_genre.GENRE.api, [])
        if genres:
            queries = [
                self.query.make_insertq(
                    self.film_genre,
                    {},
                    extra_attrs={
                        self.film_genre.ID.name: id,
                        self.film_genre.GENRE.name: genre,
                    },
                )
                for genre in genres
            ]

            tasks = [asyncio.create_task(self._execute(q, *v)) for q, v in queries]
            await asyncio.gather(*tasks)

    async def insert_countries(
        self,
        json_data: dict,
        id: int,
    ) -> None:
        countries = json_data.get(self.film_country.COUNTRY.api, [])
        if countries:
            queries = [
                self.query.make_insertq(
                    self.film_country,
                    {},
                    extra_attrs={
                        self.film_country.ID.name: id,
                        self.film_country.COUNTRY.name: country,
                    },
                )
                for country in countries
            ]

            tasks = [asyncio.create_task(self._execute(q, *v)) for q, v in queries]
            await asyncio.gather(*tasks)

    async def insert_poster(self, id: int, path: str) -> None:
        async with self._pool.acquire() as connection:
            connection: Connection

            query = self.query.make_insertq(
                self.film_poster,
                {},
                extra_attrs={
                    self.film_poster.ID.name: id,
                    self.film_poster.IMAGE_PATH.name: path,
                },
            )
            await connection.execute(query, id, path)

    async def insert_film(self, json_data: dict) -> None:
        async with self._pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                slug_value = await self.create_slug(json_data)

                qfilm, vfilm = self.query.make_insertq(
                    self.film,
                    json_data,
                    self.film.ID.name,
                    extra_attrs={self.film.SLUG.name: slug_value},
                )

                id = await connection.fetchval(qfilm, *vfilm)

                qfilm_stat, vfilm_stat = self.query.make_insertq(
                    self.film_stat,
                    json_data,
                    extra_attrs={self.film_stat.ID.name: id},
                )

                qfilm_data, vfilm_data = self.query.make_insertq(
                    self.film_data,
                    json_data,
                    extra_attrs={self.film_stat.ID.name: id},
                )

                await connection.execute(qfilm_stat, *vfilm_stat)
                await connection.execute(qfilm_data, *vfilm_data)

        await self.insert_genres(json_data, id)
        await self.insert_countries(json_data, id)

        return id

    async def get_film_by_slug(self, slug: str) -> dict:
        async with self._pool.acquire() as connection:
            connection: Connection

            query = f"""SELECT*FROM {self.film.TABLE_NAME}
                    LEFT JOIN {self.film_data.TABLE_NAME} USING({self.film_data.ID.name})
                    LEFT JOIN {self.film_stat.TABLE_NAME} USING({self.film_stat.ID.name})
                    WHERE {self.film.SLUG.name} = '{slug}';
                    """

            data = await connection.fetchrow(query)
            return data

    async def extract_genre(self, genre: str) -> dict:
        async with self._pool.acquire() as connection:
            connection: Connection

            query = f"""SELECT*FROM {self.film_genre.TABLE_NAME}
                    LEFT JOIN {self.film.TABLE_NAME} USING ({self.film.ID.name})
                    WHERE {self.film_genre.GENRE.name} = '{genre}';
                    """

            data = await connection.fetch(query)
            return data

    async def text_search(self, text: str) -> dict:
        async with self._pool.acquire() as connection:
            connection: Connection

            query = f"""SELECT*FROM {self.film.TABLE_NAME}
                    WHERE {self.film.TEXT_SEARCH_RU.name} @@ websearch_to_tsquery('russian', '{text}')
                    LIMIT 10;
                    """

            data = await connection.fetch(query)
            return data


async def test_insert(json_data: dict):
    DBI = DataBaseInterface(config, 6)
    await DBI.create_pool()
    await DBI.insert_film(json_data)

    await DBI.destroy_pool()


async def test_select():
    DBI = DataBaseInterface(config, 6)

    await DBI.create_pool()

    # data = await DBI.get_film_by_slug("the-shawshank-redemption")
    # data = await DBI.extract_genre("комедия")
    data = await DBI.text_search("форрест")
    print(data)

    await DBI.destroy_pool()


if __name__ == "__main__":
    config = load_config()

    # db_init = FilmSearchDBInit(config)
    # asyncio.run(db_init.init_tables())

    asyncio.run(test_select())

    # ids = [326, 329, 342, 361, 370, 435, 448, 3498, 258687, 535341]

    # for id in ids:
    #     with open(
    #         f"/home/mainus/Projects/FilmSearch/filmsearch/data/jsons/{id}.json", "rb"
    #     ) as file:
    #         json_data = json.loads(file.read())

    #     asyncio.run(test_insert(json_data))
