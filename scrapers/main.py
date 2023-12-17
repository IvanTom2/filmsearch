from fastapi import FastAPI
from kinopoisk import KPScraper


app = FastAPI()
kp = KPScraper("0ba6ea1c-e34f-43e3-8da5-7041b14cbbfe", 10, 3)


@app.get("/kp/film_info/{film_id}")
async def film_info(film_id: int):
    data = await kp.get_info(film_id)
    return data


@app.get("/kp/film_poster/{film_id}")
async def poster(film_id: int):
    data = await kp.get_image(film_id)
    return data
