from typing import Callable

from tortoise import Tortoise

from src.config.tortoise_config import TORTOISE_ORM


def create_start_app_handler() -> Callable:
    async def startup():
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()

    return startup


def create_stop_app_handler() -> Callable:
    async def shutdown():
        await Tortoise.close_connections()

    return shutdown
