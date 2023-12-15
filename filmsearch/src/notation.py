class Notation:
    TABLE_NAME: str
    EXCLUDE: set[str] = {"EXCLUDE", "TABLE_NAME"}

    mapper = {}
    reversed_mapper = {}

    def __init__(self) -> None:
        self.columns = self._set_up_columns()

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
    def _set_up_columns(self) -> list[str]:
        columns = [
            v for k, v in self.__dict__.items() if k.isupper() and k not in self.EXCLUDE
        ]
        return columns


class Film(Notation):
    TABLE_NAME = "film"

    ID = "id"
    KP_ID = "kp_id"
    IMDB_ID = "imdb_id"

    NAME_RU = "name_ru"
    NAME_ENG = "name_eng"
    NAME_ORIGINAL = "name_original"

    YEAR = "year"
    TYPE = "type"
    LENGTH = "lenght"

    SLUG = "slug"

    mapper = {
        ID: None,
        KP_ID: "kinopoiskId",
        IMDB_ID: "imdbId",
        NAME_RU: "nameRu",
        NAME_ENG: "nameEn",
        NAME_ORIGINAL: "nameOriginal",
        YEAR: "year",
        TYPE: "type",
        LENGTH: "filmLength",
        SLUG: None,
    }

    reversed_mapper = {
        "kinopoiskId": KP_ID,
        "imdbId": IMDB_ID,
        "nameRu": NAME_RU,
        "nameEn": NAME_ENG,
        "nameOriginal": NAME_ORIGINAL,
        "year": YEAR,
        "type": TYPE,
        "filmLength": LENGTH,
    }


class FilmStat(Notation):
    TABLE_NAME = "film_stat"

    ID = "id"

    KP_REVIEWS_COUNT = "kp_reviews_count"
    KP_GOOD_REVIEWS_COUNT = "kp_good_reviews_count"
    KP_REVIEWS_RATE = "kp_reviews_rate"

    KP_RATE = "kp_rate"
    IMDB_RATE = "imdb_rate"
    WORLD_CRITICS_RATE = "world_critics_rate"
    RF_CRITICS_RATE = "rf_critics_rate"

    KP_VOTES = "kp_votes"
    IMDB_VOTES = "imdb_votes"
    WORLD_CRITICS_VOTES = "world_critics_votes"
    RF_CRITICS_VOTES = "rf_critics_votes"

    mapper = {
        ID: None,
        KP_REVIEWS_COUNT: "reviewsCount",
        KP_GOOD_REVIEWS_COUNT: "ratingGoodReviewVoteCount",
        KP_REVIEWS_RATE: "ratingGoodReview",
        KP_RATE: "ratingKinopoisk",
        IMDB_RATE: "ratingImdb",
        WORLD_CRITICS_RATE: "ratingFilmCritics",
        RF_CRITICS_RATE: "ratingRfCritics",
        KP_VOTES: "ratingKinopoiskVoteCount",
        IMDB_VOTES: "ratingImdbVoteCount",
        WORLD_CRITICS_VOTES: "ratingFilmCriticsVoteCount",
        RF_CRITICS_VOTES: "ratingRfCriticsVoteCount",
    }

    reversed_mapper = {
        "reviewsCount": KP_REVIEWS_COUNT,
        "ratingGoodReviewVoteCount": KP_GOOD_REVIEWS_COUNT,
        "ratingGoodReview": KP_REVIEWS_RATE,
        "ratingKinopoisk": KP_RATE,
        "ratingImdb": IMDB_RATE,
        "ratingFilmCritics": WORLD_CRITICS_RATE,
        "ratingRfCritics": RF_CRITICS_RATE,
        "ratingKinopoiskVoteCount": KP_VOTES,
        "ratingImdbVoteCount": IMDB_VOTES,
        "ratingFilmCriticsVoteCount": WORLD_CRITICS_VOTES,
        "ratingRfCriticsVoteCount": RF_CRITICS_VOTES,
    }


class FilmData(Notation):
    TABLE_NAME = "film_data"

    ID = "id"

    SLOGAN = "slogan"
    DESCRIPTION = "description"
    SHORT_DESCROPTION = "short_description"

    MPAA = "mpaa"
    AGE_LIMIT = "age_limit"

    COUNTRIES = "countries"
    GENRES = "genres"

    mapper = {
        ID: None,
        SLOGAN: "slogan",
        DESCRIPTION: "description",
        SHORT_DESCROPTION: "shortDescription",
        MPAA: "ratingMpaa",
        AGE_LIMIT: "ratingAgeLimits",
        COUNTRIES: "countries",
        GENRES: "genres",
    }

    reversed_mapper = {
        "slogan": SLOGAN,
        "description": DESCRIPTION,
        "shortDescription": SHORT_DESCROPTION,
        "ratingMpaa": MPAA,
        "ratingAgeLimits": AGE_LIMIT,
        "countries": COUNTRIES,
        "genres": GENRES,
    }


if __name__ == "__main__":
    film = FilmData()
    print(film.api_mapper(film.COUNTRIES))
