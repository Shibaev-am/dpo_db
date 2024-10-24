from tortoise import fields
from tortoise.models import Model

class User(Model): # Пользователь
    id = fields.IntField(pk=True)
    
    login = fields.CharField(max_length=255, null=False)
    password = fields.CharField(max_length=255, null=False)
    
    class Meta:
        table = "_system_users"
        schema = "dpo"
        
        
class RefreshToken(Model): # Refresh token
    token = fields.CharField(pk=True, max_length=255)
    
    valid_untill = fields.DateField(null=False)
    user = fields.ForeignKeyField(
        'models.User',
        related_name='token',
        null=False,
        on_delete=fields.CASCADE
    )
    
    class Meta:
        table = "_system_tokens"
        schema = "dpo"