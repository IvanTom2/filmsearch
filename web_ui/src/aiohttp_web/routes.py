from fastapi import APIRouter
from aiohttp.web import Application
from web_ui.src.aiohttp_web.views import SiteHandler

router = APIRouter()


def old_setup_routes(
    app: Application,
    handler: SiteHandler,
    project_root,
):
    router = app.router

    router.add_get("/", handler.menu, name="menu")

    router.add_get("/login", handler.login, name="login")
    router.add_get("/register", handler.register, name="register")
    router.add_get("/account", handler.account, name="account")

    router.add_get("/genres", handler.default_genre, name="default_genre")
    router.add_get("/genres/{genre_name}", handler.genre, name="genre")

    router.add_get("/search", handler.search, name="text_search")
    router.add_get("/esearch", handler.extended_search, name="extended_search")

    router.add_static("/static/", path=project_root / "static", name="static")
