import asyncio

from tortoise import run_async, Tortoise
from settings import Settings
from app import app
from utils.logger import logger
from tortoise.contrib.fastapi import register_tortoise


logger.info("[main] Loading Tortoise ORM...")

register_tortoise(
    app,
    db_url=f"postgres://{Settings.POSTGRES_USER}:{Settings.POSTGRES_PASSWORD.get_secret_value()}@{Settings.POSTGRES_HOST}:{Settings.POSTGRES_PORT}/{Settings.POSTGRES_DB}",
    modules={"models": ["models.dpo", "models.system"]},
    generate_schemas=True,
    add_exception_handlers=True,
)
