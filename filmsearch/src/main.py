from pathlib import Path

from db import load_config


SRC_PATH = Path(__file__).parent
PROJ_PATH = SRC_PATH.parent


config = load_config(PROJ_PATH)

DB_POSTGRES: str = config["DB_POSTGRES"]
DB_POSTGRES_PASSWORD: str = config["DB_POSTGRES_PASSWORD"]

DB_USERNAME: str = config["DB_USERNAME"]
DB_PASSWORD: str = config["DB_PASSWORD"]
DB_HOST: str = config["DB_HOST"]
DB_PORT: int = config["DB_PORT"]
