from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from pathlib import Path

from src.filmsearch_api import Genres, FilmSearchAPI

IMAGE_PATH = Path(__file__).parent / "static/images"

genres = Genres()
api = FilmSearchAPI("http://127.0.0.1:8001")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await api.create_session()

    yield

    await api.destroy_session()


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse, name="menu")
async def menu(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


@app.get("/account", name="account")
async def account_page(request: Request):
    return templates.TemplateResponse(
        "account.html",
        {"request": request},
    )


@app.get("/login", name="login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@app.get("/register", name="register")
async def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@app.get("/genres", name="default_genre")
async def default_genre_page(request: Request):
    default = genres.default.url
    return RedirectResponse(url=f"/genres/{default}")


@app.get("/genres/{genre_url}", name="genres")
async def genres_page(request: Request, genre_url: str):
    genre = genres.map(genre_url)
    films = await api.films_by_genre(genre.api)

    return templates.TemplateResponse(
        "genres.html",
        {
            "request": request,
            "genres": genres.all,
            "selected_genre": genre.ui,
            "films": films,
        },
    )


@app.get("/film/{slug}")
async def film_page(request: Request, slug: str):
    film = await api.get_film(slug)
    image_path = f"{film['kp_id']}.jpg"

    return templates.TemplateResponse(
        "film.html",
        {
            "request": request,
            "film": film,
            "image_path": image_path,
        },
    )


@app.get("/search", name="text_search")
async def text_search_page(request: Request, query: str):
    films = await api.text_search(query)

    return templates.TemplateResponse(
        "text_search.html",
        {
            "request": request,
            "films": films,
        },
    )


@app.get("/esearch", name="extended_search")
async def extended_search_page(request: Request):
    return templates.TemplateResponse(
        "extended_search.html",
        {"request": request},
    )
