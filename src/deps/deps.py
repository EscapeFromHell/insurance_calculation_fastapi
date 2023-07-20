from fastapi import Depends
from tortoise import Tortoise

from src.core.repository import RateRepo


def get_db() -> Tortoise:
    return Tortoise.get_connection("default")


def rate_repo(db: Tortoise = Depends(get_db)) -> RateRepo:
    return RateRepo(db)
