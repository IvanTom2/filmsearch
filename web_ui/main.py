from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static/css", StaticFiles(directory="static/css"), name="css")


@app.get("/", response_class=HTMLResponse, name="menu")
async def menu(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


@app.get("/account", name="account")
async def account(request: Request):
    return templates.TemplateResponse(
        "account.html",
        {"request": request},
    )


@app.get("/login", name="login")
async def login(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request},
    )


@app.get("/register", name="register")
async def register(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request},
    )


@app.get("/genres", name="default_genre")
async def default_genre(request: Request):
    default = "comedy"
    return RedirectResponse(url=f"/genres/{default}")


@app.get("/genres/{genre_name}", name="genres")
async def genres(request: Request, genre_name: str):
    return templates.TemplateResponse(
        "genres.html",
        {
            "request": request,
            "genre": genre_name,
        },
    )


@app.get("/search", name="text_search")
async def text_search(request: Request):
    return templates.TemplateResponse(
        "text_search.html",
        {"request": request},
    )


@app.get("/esearch", name="extended_search")
async def extended_search(request: Request):
    return templates.TemplateResponse(
        "extended_search.html",
        {"request": request},
    )
