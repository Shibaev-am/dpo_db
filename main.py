import asyncio
import jwt
from tortoise import Tortoise, run_async, connections
import models_dpo
from config import JWT_EXPIRE, JWT_SECRET, ACCESS_EXPIRE, TORTOISE_ORM
import os
import inspect
from cachetools import TTLCache
import bcrypt
import secrets
from datetime import datetime, timedelta, timezone
import hashlib

from fastapi import FastAPI, Query
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List, Dict, Any
from pydantic import BaseModel, SecretStr
from tortoise.transactions import in_transaction
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from models_system import RefreshToken, User

app = FastAPI()

origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app = FastAPI()

class_maping = {name: cls for name, cls in inspect.getmembers(models_dpo, inspect.isclass)}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
cache = TTLCache(maxsize=1024, ttl=ACCESS_EXPIRE)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if token in cache:
        return token
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={'error': 'Invalid token'},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.get("/api/test_token")
def ping(token: str = Depends(get_current_user)):
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
    # print(result)
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


def hash_password_sha256(password: str) -> str:
    sha256_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return sha256_hash

def check_password(password: str, hashed: str) -> bool:
    return hash_password_sha256(password) == hashed

class AuthCredentials(BaseModel):
    login: str
    password: str

@app.post("/api/auth")
async def auth_user(payload: AuthCredentials):

    psw = payload.password
    login = payload.login
    
    user = await User.filter(login=login).first()
    
    # print(hash_password_sha256(psw))

    if user:
        if check_password(psw, user.password):
            # победа
            refresh_token = secrets.token_hex(64)
            valid_until = datetime.now().date() + timedelta(weeks=1)
            expires = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE)
            token = jwt.encode({"login": user.login, "exp": expires}, JWT_SECRET, algorithm="HS256")
            cache[token] = user.id
            await RefreshToken.create(
                token=refresh_token,
                valid_untill=valid_until,
                user_id=user.id
            )
            print('auth:')
            print({'access_token': token, 'refresh_token': refresh_token})
            return {'access_token': token, 'refresh_token': refresh_token}
        
    raise HTTPException(status_code=401, detail="Invalid credentials")
    
    
class Refresh(BaseModel):
    refresh_token: str

@app.post("/api/refresh_token")
async def refresh_tkn(
        refresh_token: Refresh=None
    ):
    old_token = refresh_token.refresh_token
    ans = await RefreshToken.filter(token=old_token).exists()
    if not ans:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={'error': 'Invalid token'},
            headers={"WWW-Authenticate": "Bearer"},
        )
    ref_tkn = await RefreshToken.filter(token=old_token).first()
    user_id = ref_tkn.user_id
    
    new_refresh_token = secrets.token_hex(64)
    user = await User.get(id=user_id)
    
    valid_until = datetime.now().date() + timedelta(weeks=1)
    expires = datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRE)
    new_token = jwt.encode({"login": user.login, "exp": expires}, JWT_SECRET, algorithm="HS256")
    cache[new_token] = user_id
    
    await RefreshToken.create(
        token=new_refresh_token,
        valid_untill=valid_until,
        user_id=user_id
    )
    await ref_tkn.delete()
    print('refresh_token:')
    print({'access_token': new_token, 'refresh_token': new_refresh_token})
    return {'access_token': new_token, 'refresh_token': new_refresh_token}    


class Entries(BaseModel):
    entries: List[Dict[str, Any]]

@app.put("/api/entry")
async def update_entity(
    entity: str = Query(...),
    entries: Entries = None,
    token: str = Depends(get_current_user)
):  
    print(entity)
    queries = entries.entries
    for query in queries:
        cls = class_maping[entity]
        primary_key_field = cls._meta.pk_attr
        print(primary_key_field)
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
# рабочий хэш(SHA256) для пароля admin          8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918