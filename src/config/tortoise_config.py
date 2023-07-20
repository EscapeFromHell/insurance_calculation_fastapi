TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "database": "insurance_calculation_fastapi",
                "host": "insurance_calculation_fastapi-db",
                "port": "5432",
                "user": "postgres",
                "password": "password",
            },
        }
    },
    "apps": {"models": {"models": ["src.core.models", "aerich.models"], "default_connection": "default"}},
}
