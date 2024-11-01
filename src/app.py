import datetime
from enum import StrEnum
import functools
import inspect
import time
from typing import Any, Dict, List, Optional
import bcrypt
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from pydantic import BaseModel
from tortoise import Model
from settings import Settings
from models.system import _SystemUser
import models.dpo
from tortoise.contrib.pydantic import pydantic_model_creator
from settings import Settings
from tortoise.contrib.fastapi import register_tortoise
from fastapi.middleware.cors import CORSMiddleware
from tortoise.expressions import Q


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    db_url=f"postgres://{Settings.POSTGRES_USER}:{Settings.POSTGRES_PASSWORD.get_secret_value()}@{Settings.POSTGRES_HOST}:{Settings.POSTGRES_PORT}/{Settings.POSTGRES_DB}",
    modules={"models": ["models.dpo", "models.system"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth")


class TokenType(StrEnum):
    REFRESH = "refresh"
    ACCESS = "access"


class Token(BaseModel):
    user_id: int
    exp: int
    type: TokenType

    @property
    def is_access(self) -> bool:
        return self.type == TokenType.ACCESS

    @property
    def is_refresh(self) -> bool:
        return self.type == TokenType.REFRESH

    @property
    def is_valid(self) -> bool:
        return self.exp > time.time()


async def get_token(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = jwt.decode(
            token,
            Settings.JWT_SECRET.get_secret_value(),
            algorithms=[Settings.JWT_ALGORITHM],
            verify_exp=True,
        )
    except jwt.DecodeError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired",
        )
    except:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
        )
    else:
        return Token(**decoded_token)


async def get_user(token: Token = Depends(get_token)):
    user = await _SystemUser.get_or_none(id=token.user_id)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )
    return user


@app.get("/api/user/me")
def get_user_me(user: _SystemUser = Depends(get_user)):
    user.password = "********"
    return user


@functools.lru_cache(maxsize=1)
def _get_entities():
    entities: List[Dict[Any, Any]] = []
    for cls in map(lambda cls_name: getattr(models.dpo, cls_name), dir(models.dpo)):
        if not isinstance(cls, type) or not issubclass(cls, Model):
            continue
        PydanticModel = pydantic_model_creator(cls, allow_cycles=False)
        model_meta = PydanticModel.model_json_schema()
        if "$defs" in model_meta:
            model_meta.pop("$defs")
        entities.append(model_meta)
    return entities


@app.get("/api/entities")
async def get_entities(user: _SystemUser = Depends(get_user)) -> List[Dict[Any, Any]]:
    classes = inspect.getmembers(models.dpo, inspect.isclass)
    entities = []
    for name, cls in classes:
        if cls == models.dpo.BaseModel or not issubclass(cls, Model):
            continue
        entities.append({
            "name": name,
            "description": getattr(cls.Meta, 'description', None)
        })
    return entities
    # return _get_entities()


class PostEntriesPayload(BaseModel):
    selector: Dict[str, Any]


@app.get("/api/entity/structure")
async def get_schema(
    entity: str = Query(...),
    user: _SystemUser = Depends(get_user),
):
    cls: Optional[type[Model]] = getattr(models.dpo, entity, None)
    if not cls:
        raise HTTPException(status_code=404, detail="Entity not found")
    schema = pydantic_model_creator(cls).model_json_schema()
    if "$defs" in schema:
        schema.pop("$defs")

    return {"schema": schema}


@app.post("/api/entry")
async def post_entries(
    payload: PostEntriesPayload,
    entity: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    user: _SystemUser = Depends(get_user),
):
    cls: Optional[type[Model]] = getattr(models.dpo, entity, None)
    if not cls:
        raise HTTPException(status_code=404, detail="Entity not found")
    cls_pedantic = pydantic_model_creator(cls)

    offset = (page - 1) * page_size
    entries = cls.filter(**payload.selector).offset(offset).limit(page_size + 1).order_by("id")
    entries = await cls_pedantic.from_queryset(entries)

    has_next = False
    if len(entries) > page_size:
        entries = entries[:page_size]
        has_next = True

    return {"entries": entries, "has_next": has_next}


async def authenticate_user(username: str, password: str):
    user = await _SystemUser.get_or_none(login=username)
    if not user:
        return False
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        return False
    return user


def create_token(user_id: int, expire_in_minutes: int, type: TokenType):
    refresh_token_expire = datetime.datetime.now() + datetime.timedelta(
        minutes=expire_in_minutes
    )
    refresh_token_expire_timestamp = int(refresh_token_expire.timestamp())
    refresh_token = Token(
        user_id=user_id, exp=refresh_token_expire_timestamp, type=type
    )
    return jwt.encode(
        refresh_token.model_dump(mode="json"),
        Settings.JWT_SECRET.get_secret_value(),
        algorithm=Settings.JWT_ALGORITHM,
    )

@app.post("/api/auth")
async def post_auth(payload: OAuth2PasswordRequestForm = Depends()):
    #! OAuth2PasswordRequestForm нужен для Swagger  https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform

    user = await authenticate_user(payload.username, payload.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    refresh_jwt_token = create_token(
        user.id, Settings.REFRESH_TOKEN_EXPIRE_MINUTES, TokenType.REFRESH
    )

    access_jwt_token = create_token(
        user.id, Settings.ACCESS_TOKEN_EXPIRE_MINUTES, TokenType.ACCESS
    )

    return {"access_token": access_jwt_token, "refresh_token": refresh_jwt_token}


class PostRefreshTokenPayload(BaseModel):
    refresh_token: str


@app.post("/api/refresh_token")
async def post_refresh_token(payload: PostRefreshTokenPayload):
    refresh_token = await get_token(payload.refresh_token)
    user = await get_user(refresh_token)

    access_jwt_token = create_token(
        user.id, Settings.ACCESS_TOKEN_EXPIRE_MINUTES, TokenType.ACCESS
    )

    return {"access_token": access_jwt_token}


class PutEntryPayload(BaseModel):
    entries: List[Dict[str, Any]]


@app.put("/api/entry")
async def put_entity(
    payload: PutEntryPayload,
    entity: str = Query(...),
    user: _SystemUser = Depends(get_user),
):
    for entry in payload.entries:
        cls: Optional[type[Model]] = getattr(models.dpo, entity, None)
        if not cls:
            raise HTTPException(status_code=404, detail="Entity not found")
        primary_key_field = cls._meta.pk_attr
        if primary_key_field in entry:
            await cls.update_or_create(
                **{primary_key_field: entry[primary_key_field]}, defaults=entry
            )
        else:
            await cls.create(**entry)


class DeleteEntryPayload(BaseModel):
    selector: Dict[str, Any]

class DeleteEntriesPayload(BaseModel):
    ids: list[int]

@app.delete("/api/entry")
async def delete_entity(
    payload: DeleteEntryPayload,
    entity: str = Query(...),
    limit: int = Query(1, ge=1),
    user: _SystemUser = Depends(get_user),
):
    cls: Optional[type[Model]] = getattr(models.dpo, entity, None)
    if not cls:
        raise HTTPException(status_code=404, detail="Entity not found")
    await cls.filter(**payload.selector).limit(limit).delete()

@app.delete("/api/entry/multiple")
async def delete_entries(
    payload: DeleteEntriesPayload,
    entity: str = Query(...),
    user: _SystemUser = Depends(get_user),
):
    cls: Optional[type[Model]] = getattr(models.dpo, entity, None)
    if not cls:
        raise HTTPException(status_code=404, detail="Entity not found")
    await cls.filter(Q(id__in=payload.ids)).delete()