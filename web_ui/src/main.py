import asyncio
import jinja2
import aiohttp_jinja2
from pathlib import Path
from aiohttp import web
from aiohttp.web import Request, Response, Application


from views import SiteHandler
from routes import setup_routes
from utils import load_config


SRC_PATH = Path(__file__).parent
PROJ_PATH = SRC_PATH.parent
TEMPL_PATH = SRC_PATH / "templates"


def setup_jinja(app: Application):
    jinja_env = aiohttp_jinja2.setup(
        app,
        loader=jinja2.FileSystemLoader(str(TEMPL_PATH)),
    )


async def init_app(loop):
    config = load_config(PROJ_PATH)
    host = config["host"]
    port = config["port"]

    app = Application(loop=loop)
    handler = SiteHandler()

    setup_jinja(app)
    setup_routes(app, handler, PROJ_PATH)
    return app, host, port


def main():
    loop = asyncio.get_event_loop()
    app, host, port = loop.run_until_complete(init_app(loop))

    web.run_app(
        app,
        host=host,
        port=port,
        loop=loop,
    )


if __name__ == "__main__":
    main()
