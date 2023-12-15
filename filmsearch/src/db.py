import json
import asyncio
import asyncpg
from pathlib import Path
from asyncio import Lock
from asyncpg import Pool, Connection
from abc import abstractmethod

from notation import Notation, Film, FilmData, FilmStat


DB_KEY = "database"


def load_config(root_path: Path = Path(__file__).parent.parent):
    with open(root_path / "config.json") as file:
        return json.load(file)


class DataBaseInit(object):
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


class FilmSearchDBInit(DataBaseInit):
    def __init__(self, DB_NAME) -> None:
        super().__init__(DB_NAME)

    async def create_film_relation(
        self,
        connection: Connection,
    ) -> None:
        query = f"""
                CREATE TABLE {Film.TABLE_NAME} (
                {Film.ID} SERIAL,
                {Film.KP_ID} INTEGER UNIQUE,
                {Film.IMDB_ID} VARCHAR NOT NULL,
                {Film.NAME_RU} VARCHAR NOT NULL,
                {Film.NAME_ENG} VARCHAR,
                {Film.NAME_ORIGINAL} VARCHAR,
                {Film.YEAR} INTEGER NOT NULL,
                {Film.TYPE} VARCHAR NOT NULL,
                {Film.LENGTH} INTEGER NOT NULL,
                {Film.SLUG} VARCHAR UNIQUE,
                PRIMARY KEY ({Film.ID})
                );
                """
        await self.create_new_table(connection, query)

    async def create_film_stat_relation(
        self,
        connection: Connection,
    ) -> None:
        query = f"""
                CREATE TABLE {FilmStat.TABLE_NAME} (
                {FilmStat.ID} INTEGER,
                {FilmStat.KP_REVIEWS_COUNT} INTEGER,
                {FilmStat.KP_GOOD_REVIEWS_COUNT} INTEGER,
                {FilmStat.KP_REVIEWS_RATE} FLOAT,
                {FilmStat.KP_RATE} FLOAT,
                {FilmStat.IMDB_RATE} FLOAT,
                {FilmStat.WORLD_CRITICS_RATE} FLOAT,
                {FilmStat.RF_CRITICS_RATE} FLOAT,
                {FilmStat.KP_VOTES} INTEGER,
                {FilmStat.IMDB_VOTES} INTEGER,
                {FilmStat.WORLD_CRITICS_VOTES} INTEGER,
                {FilmStat.RF_CRITICS_VOTES} INTEGER,
                FOREIGN KEY ({FilmStat.ID})
                    REFERENCES {Film.TABLE_NAME}({Film.ID})
                );
                """
        await self.create_new_table(connection, query)

    async def create_film_data_relation(
        self,
        connection: Connection,
    ) -> None:
        query = f"""
                CREATE TABLE {FilmData.TABLE_NAME} (
                {FilmData.ID} INT,
                {FilmData.SLOGAN} TEXT,
                {FilmData.DESCRIPTION} TEXT,
                {FilmData.SHORT_DESCROPTION} TEXT,
                {FilmData.MPAA} INTEGER,
                {FilmData.AGE_LIMIT} INTEGER,
                {FilmData.COUNTRIES} VARCHAR[],
                {FilmData.GENRES} VARCHAR[],
                FOREIGN KEY ({FilmData.ID})
                    REFERENCES {Film.TABLE_NAME}({Film.ID})
                );
                """
        await self.create_new_table(connection, query)

    async def init_tables(self) -> None:
        try:
            await self._database_initiation()

            connection = await self._user_conn()
            await self.create_film_relation(connection)
            await self.create_film_stat_relation(connection)
            await self.create_film_data_relation(connection)

        finally:
            if not connection.is_closed():
                await connection.close()


class Query(object):
    def __init__(self) -> None:
        self.film = Film()
        self.film_stat = FilmStat()
        self.film_data = FilmData()

    def insert_allocate(
        self,
        query: str,
        note_obj: Notation,
        json_data: dict,
    ) -> dict:
        columns = note_obj.columns
        data = {
            col: json_data.get(note_obj.api_mapper(col))
            for col in columns
            if json_data.get(note_obj.api_mapper(col)) is not None
        }

        attr_str = "(" + ",".join(list(data.keys())) + ")"
        val_str = "(" + ",".join(list(data.values())) + ")"

        query = query + attr_str + " VALUES" + val_str
        return query

    def insert_film_query(self, json_data: dict):
        query = f"INSERT INTO {Film.TABLE_NAME}"
        query = self.insert_allocate(query, self.film, json_data)

        print(query)

        return query


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

    def insert_film(self, json_data: dict) -> None:
        query = self.query.insert_film_query(json_data)


if __name__ == "__main__":
    config = load_config()

    # db_init = FilmSearchDBInit(config)
    # asyncio.run(db_init.init_tables())

    with open("/home/mainus/Projects/FilmSearch/film.json", "rb") as file:
        json_data = json.loads(file.read())

    DBI = DataBaseInterface(config, 6)
    DBI.insert_film(json_data)
