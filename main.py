import asyncio
from tortoise import Tortoise, run_async, connections
import models_dpo
from config import TORTOISE_ORM
import os
import inspect


from fastapi import FastAPI, Query
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from typing import List, Dict, Any
from pydantic import BaseModel
from tortoise.transactions import in_transaction
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

classes = [cls for name, cls in inspect.getmembers(models_dpo, inspect.isclass)]
# TODO: доделать маппинг
class_maping = {'File': models_dpo.File}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

# TODO: сделать норм авторизацию и эндпоинт /auth
async def get_current_user(token: str = Depends(oauth2_scheme)):
    ACCESS_TOKEN = "secret_token_123"
    print(token)
    if token != ACCESS_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

    
@app.get("/ping")
def ping():
    return {'success': True}


@app.get("/api/entities")
async def get_tables(token: str = Depends(get_current_user)):
    result = {}
    for cls in classes:
        if cls.__name__ == "Model":
            continue
        PydanticModel = pydantic_model_creator(cls)
        model_meta = PydanticModel.model_json_schema()
        result[cls.__name__] = model_meta
    
    return result


class Selector(BaseModel):
    selector: Dict[str, Any]


@app.post("/api/entry")
async def get_tables(
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
        # TODO: заменить file_id на pk
        if 'file_id' in query:
            old_object = await cls.get(file_id=query['file_id'])
            query.pop('file_id')
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