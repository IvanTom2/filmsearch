class Generated(object):
    def __init__(self, query: str) -> None:
        self.query = query


class Type(object):
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"

    VARCHAR = "VARCHAR"
    TEXT = "TEXT"

    SERIAL = "SERIAL"
    ARRAY_VARCHAR = "VARCHAR[]"
    ARRAY_INTEGER = "INTEGER[]"

    TSVECTOR = "tsvector"

    default = {
        FLOAT,
        INTEGER,
    }

    strings = {
        VARCHAR,
        TEXT,
    }

    arrays = {
        ARRAY_VARCHAR,
    }


class Attribute(object):
    """
    db - attribute name in db
    api - attribute name in api
    dtype - attribute type in db
    """

    def __init__(
        self,
        name: str,
        api: str | None,
        dtype: Type,
        unpack=None,
        generated: Generated = None,
    ) -> None:
        self.name = name
        self.api = api
        self.dtype = dtype
        self.unpack = unpack
        self.generated = generated

    def conv(self, value) -> str:
        """Convert value for db insert"""
        if self.dtype in Type.arrays:
            value = list(map(lambda x: x[self.unpack], value))

        return value

    @property
    def db(self) -> str:
        """Return name + type for db init"""
        db = self.name + " " + self.dtype
        if isinstance(self.generated, Generated):
            db += " " + self.generated.query

        return db


class Model:
    TABLE_NAME: str
    EXCLUDE: set[str] = {"EXCLUDE", "TABLE_NAME"}

    mapper = {}
    reversed_mapper = {}

    def __init__(self) -> None:
        self.attributes = self._set_up_attributes()

    @classmethod
    def api_mapper(
        self,
        column: str,
        reverse: bool = False,
        default=None,
    ):
        if reverse:
            return self.reversed_mapper.get(column, default)
        else:
            return self.mapper.get(column, default)

    @classmethod
    def _set_up_attributes(self) -> list[Attribute]:
        columns = [
            v for k, v in self.__dict__.items() if k.isupper() and k not in self.EXCLUDE
        ]
        return columns


class Film(Model):
    TABLE_NAME = "film"

    ID = Attribute("id", None, Type.SERIAL)
    KP_ID = Attribute("kp_id", "kinopoiskId", Type.INTEGER)
    IMDB_ID = Attribute("imdb_id", "imdbId", Type.VARCHAR)

    NAME_RU = Attribute("name_ru", "nameRu", Type.VARCHAR)
    NAME_ENG = Attribute("name_eng", "nameEn", Type.VARCHAR)
    NAME_ORIGINAL = Attribute("name_original", "nameOriginal", Type.VARCHAR)

    YEAR = Attribute("year", "year", Type.INTEGER)
    TYPE = Attribute("type", "type", Type.VARCHAR)
    LENGTH = Attribute("lenght", "filmLength", Type.INTEGER)

    MPAA = Attribute("mpaa", "ratingMpaa", Type.VARCHAR)
    AGE_LIMIT = Attribute("age_limit", "ratingAgeLimits", Type.VARCHAR)

    SLUG = Attribute("slug", None, Type.VARCHAR)

    TEXT_SEARCH_RU = Attribute(
        "txtsrch_ru",
        None,
        Type.TSVECTOR,
        generated=Generated(
            f"GENERATED ALWAYS AS (to_tsvector('russian', {NAME_RU.name})) STORED",
        ),
    )


class FilmStat(Model):
    TABLE_NAME = "film_stat"

    ID = Attribute(
        "id",
        None,
        Type.INTEGER,
    )

    KP_REVIEWS_COUNT = Attribute(
        "kp_reviews_count",
        "reviewsCount",
        Type.INTEGER,
    )
    KP_GOOD_REVIEWS_COUNT = Attribute(
        "kp_good_reviews_count",
        "ratingGoodReviewVoteCount",
        Type.INTEGER,
    )
    KP_REVIEWS_RATE = Attribute(
        "kp_reviews_rate",
        "ratingGoodReview",
        Type.FLOAT,
    )

    KP_RATE = Attribute(
        "kp_rate",
        "ratingKinopoisk",
        Type.FLOAT,
    )
    IMDB_RATE = Attribute(
        "imdb_rate",
        "ratingImdb",
        Type.FLOAT,
    )
    WORLD_CRITICS_RATE = Attribute(
        "world_critics_rate",
        "ratingFilmCritics",
        Type.FLOAT,
    )
    RF_CRITICS_RATE = Attribute(
        "rf_critics_rate",
        "ratingRfCritics",
        Type.FLOAT,
    )

    KP_VOTES = Attribute(
        "kp_votes",
        "ratingKinopoiskVoteCount",
        Type.INTEGER,
    )
    IMDB_VOTES = Attribute(
        "imdb_votes",
        "ratingImdbVoteCount",
        Type.INTEGER,
    )
    WORLD_CRITICS_VOTES = Attribute(
        "world_critics_votes",
        "ratingFilmCriticsVoteCount",
        Type.INTEGER,
    )
    RF_CRITICS_VOTES = Attribute(
        "rf_critics_votes",
        "ratingRfCriticsVoteCount",
        Type.INTEGER,
    )


class FilmData(Model):
    TABLE_NAME = "film_data"

    ID = Attribute("id", None, Type.INTEGER)

    SLOGAN = Attribute("slogan", "slogan", Type.TEXT)
    DESCRIPTION = Attribute("description", "description", Type.TEXT)
    SHORT_DESCROPTION = Attribute("short_description", "shortDescription", Type.TEXT)


class FilmPoster(Model):
    TABLE_NAME = "film_poster"

    ID = Attribute("id", None, Type.INTEGER)
    IMAGE_PATH = Attribute("img_path", None, Type.VARCHAR)


class FilmGenre(Model):
    TABLE_NAME = "film_genre"

    ID = Attribute("id", None, Type.INTEGER)
    GENRE = Attribute("genre", "genres", Type.VARCHAR)


class FilmCountry(Model):
    TABLE_NAME = "film_country"

    ID = Attribute("id", None, Type.INTEGER)
    COUNTRY = Attribute("country", "countries", Type.VARCHAR)


if __name__ == "__main__":
    film = Film()

    print(film.TEXT_SEARCH_RU.db)
