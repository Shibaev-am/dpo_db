# config.py

TORTOISE_ORM = {
    "connections": {
        "default": "postgres://postgres:1234@localhost:9090/dpo_db?schema=dpo"
    },
    "apps": {
        "models": {
            "models": ["models_dpo", "models_system"],
            "default_connection": "default",
        },
    }
}
