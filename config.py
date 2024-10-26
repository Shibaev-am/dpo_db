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

JWT_SECRET = "53660323d357e45a896861effb034cd95dd752fa2b6443a1860789dfcb8a6cea"
JWT_EXPIRE = 10080 # 1 week
ACCESS_EXPIRE = 600