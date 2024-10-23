import asyncio
from tortoise import Tortoise, run_async, connections
import models_dpo
from config import TORTOISE_ORM
import os
import inspect
from cachetools import TTLCache
import bcrypt
import secrets
from datetime import datetime, timedelta

from fastapi import FastAPI, Query
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List, Dict, Any
from pydantic import BaseModel, SecretStr
from tortoise.transactions import in_transaction
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(
        db_url="postgres://postgres:1234@localhost:9090/dpo_db?schema=dpo", 
        modules={"models": ["models_dpo"]}
    )
    conn = Tortoise.get_connection("default")
    await conn.execute_script("CREATE SCHEMA IF NOT EXISTS dpo;") 
    await Tortoise.generate_schemas(safe=True)
    yield

app = FastAPI(lifespan=lifespan)

class_maping = {name: cls for name, cls in inspect.getmembers(models_dpo, inspect.isclass)}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
cache = TTLCache(maxsize=1024, ttl=600)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    # ACCESS_TOKEN = "secret_token_123"
    # print(token)
    # if token != ACCESS_TOKEN:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid token",
    #         headers={"WWW-Authenticate": "Bearer"},
    #     )
    # return token
    if token in cache:
        return token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={'error': 'Invalid token'},
        headers={"WWW-Authenticate": "Bearer"},
    )

    
@app.get("/ping")
def ping():
    return {'success': True}


@app.get("/api/entities")
async def get_tables(token: str = Depends(get_current_user)):
    result = {}
    for name, cls in class_maping.items():
        if name == "Model":
            continue
        PydanticModel = pydantic_model_creator(cls)
        model_meta = PydanticModel.model_json_schema()
        result[name] = model_meta
    
    return result


class Selector(BaseModel):
    selector: Dict[str, Any]

@app.post("/api/entry")
async def get_entries(
        entity: str = Query(...),
        page: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=100),
        entity_data: Selector = None,
        token: str = Depends(get_current_user)
    ):
    filter = entity_data.selector
    cls = class_maping[entity]

    total_count = await cls.filter(**filter).count()
    if total_count == 0:
        return {'entries': []}
    
    offset = (page - 1) * page_size
    if (page - 1) * page_size >= total_count:
        offset = (total_count // page_size) * page_size
    objects = cls.filter(**filter).all().offset(offset).limit(page_size)
    
    cls_pedantic = pydantic_model_creator(cls)
    result = await cls_pedantic.from_queryset(objects)
    return {'entries': result, 'pages': page}


class AuthCredentials(BaseModel):
    user: str
    password: str

@app.post("/api/auth")
async def auth_user(
        credentials: AuthCredentials=None
    ):
    login = credentials['login']
    psw = bcrypt.hashpw(credentials['password'].encode('utf-8'), bcrypt.gensalt())
    
    users = class_maping("User").filter(login=login)
    for user in users:
        password = user.password
        if bcrypt.checkpw(psw, password):
            # победа
            token = secrets.token_hex(32)
            refresh_token = secrets.token_hex(32)
            cache[token] = user.user_id
            valid_until = datetime.now().date() + timedelta(weeks=1)
            await class_maping['RefreshToken'].create(
                token=refresh_token,
                valid_untill=valid_until,
                user_id=user.user_id
            )
            
            return {'access_token': token, 'refresh_token': refresh_token}
        
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={'error': 'Invalid token'},
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    
class Refresh(BaseModel):
    refresh_token: str

@app.post("/api/refresh_token")
async def refresh_tkn(
        refresh_token: Refresh=None
    ):
    old_token = refresh_token['refresh_token']
    ans = await class_maping['RefreshToken'].filter(token=old_token).exists()
    if not ans:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={'error': 'Invalid token'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    ref_tkn = await class_maping['RefreshToken'].filter(token=old_token).first()
    user_id = ref_tkn.user_id
    
    new_token = secrets.token_hex(32)
    new_refresh_token = secrets.token_hex(32)
    cache[new_token] = user_id
    valid_until = datetime.now().date() + timedelta(weeks=1)
    
    await class_maping['RefreshToken'].create(
        token=new_refresh_token,
        valid_untill=valid_until,
        user_id=user_id
    )
    await ref_tkn.delete()
    return {'access_token': new_token, 'refresh_token': new_refresh_token}    


class Entries(BaseModel):
    entries: List[Dict[str, Any]]

@app.put("/api/entry")
async def update_entity(
    entity: str = Query(...),
    entries: Entries = None,
    token: str = Depends(get_current_user)
):  
    queries = entries.entries
    for query in queries:
        cls = class_maping[entity]
        primary_key_field = cls._meta.pk_attr
        if primary_key_field in query:
            old_object = await cls.get(file_id=query[primary_key_field])
            query.pop(primary_key_field)
            await old_object.update_from_dict(query)
            await old_object.save()
            print('обновили объект')
        else:
            await cls.create(**query)
            print('создали объект')
    return {'success': True}


@app.delete("/api/entry")
async def delete_entity(
    entity: str = Query(...),
    limit: int = Query(1, ge=1),
    entity_data: Selector = None,
    token: str = Depends(get_current_user)
):  
    filter = entity_data.selector
    cls = class_maping[entity]
    
    async with in_transaction():
        await cls.filter(**filter).limit(limit).delete()
        
    return {'success': True}
       
    
register_tortoise(
    app,
    db_url="postgres://postgres:1234@localhost:9090/dpo_db?schema=dpo", 
    modules={"models": ["models_dpo", "models_system"]},
    generate_schemas=True,
    add_exception_handlers=True,
)   

#  uvicorn main:app --reload