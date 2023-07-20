from tortoise import Tortoise


class Repository:
    def __init__(self, db: Tortoise):
        self.db: Tortoise = db
