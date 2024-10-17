import asyncio
from tortoise import Tortoise, run_async, connections
from models_dpo import *
from config import TORTOISE_ORM
import os
from faker import Faker 
from tortoise.utils import get_schema_sql
import random
from datetime import timedelta

async def init_db():
    # Инициализация подключения к базе данных
    await Tortoise.init(config=TORTOISE_ORM)

    conn = Tortoise.get_connection("default")
    await conn.execute_script("CREATE SCHEMA IF NOT EXISTS dpo;")    
    

    await Tortoise.generate_schemas(safe=True)
    

    


async def main():
    await init_db()
    
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
    
    
    
