from typing import Any, ClassVar
from tortoise import models


class BaseModel(models.Model):
    Meta: ClassVar[type[Any]]  # type: ignore
