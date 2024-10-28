from tortoise import fields
from tortoise.models import Model


class _SystemUser(Model):  # Пользователь
    id = fields.IntField(pk=True)

    login = fields.CharField(max_length=255, null=False)
    password = fields.CharField(max_length=255, null=False)
