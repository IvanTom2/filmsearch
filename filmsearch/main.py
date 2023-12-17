import sys
import asyncio
from pathlib import Path
from fastapi import FastAPI
from contextlib import asynccontextmanager

sys.path.append(str(Path(__file__).parent / "src"))
from src.db import load_config, DataBaseInterface

PROJ_PATH = Path(__file__).parent
SRC_PATH = PROJ_PATH / "src"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.create_pool()

    yield

    await db.destroy_pool()


config = load_config(PROJ_PATH)
db = DataBaseInterface(config, 6)
app = FastAPI(lifespan=lifespan)


@app.get("/film/{slug}")
async def film(slug: str):
    data = await db.get_film_by_slug(slug)
    return data


@app.get("/genres/{genre}")
async def film(genre: str):
    data = await db.extract_genre(genre)
    return data


@app.get("/text_search/{text}")
async def film(text: str):
    data = await db.text_search(text)
    return data
