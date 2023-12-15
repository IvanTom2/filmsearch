import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import Request, Response, HTTPFound


class SiteHandler:
    @aiohttp_jinja2.template("index.html")
    async def menu(self, request: Request) -> Response:
        return {}

    @aiohttp_jinja2.template("account.html")
    async def account(self, request: Request) -> Response:
        return {}

    @aiohttp_jinja2.template("login.html")
    async def login(self, request: Request) -> Response:
        return {}

    @aiohttp_jinja2.template("register.html")
    async def register(self, request: Request) -> Response:
        return {}

    async def default_genre(self, request: Request) -> Response:
        default = "comedy"
        location = request.app.router["genre"].url_for(genre_name=default)
        return HTTPFound(location)

    @aiohttp_jinja2.template("genres.html")
    async def genre(self, request: Request) -> Response:
        genre = request.match_info["genre_name"]
        return {"genre": genre}

    @aiohttp_jinja2.template("extendeted_search.html")
    async def extended_search(self, request: Request) -> Response:
        return {}

    @aiohttp_jinja2.template("text_search.html")
    async def search(self, request: Request) -> Response:
        query = request.query.get("query", "")
        return {"query": query}
