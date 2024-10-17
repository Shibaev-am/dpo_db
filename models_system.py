from tortoise import fields, models
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    
    login = fields.CharField(max_length=255, null=False)
    password = fields.CharField(max_length=255, null=False)
    
    class Meta:
        table = "_system_users"
        schema = "dpo"
        
        
class RefreshToken(Model):
    token = fields.CharField(pk=True, max_length=255)
    
    valid_untill = fields.DateField(null=False)
    user_id = fields.ForeignKeyField(
        'models.User',
        related_name='token',
        null=False,
        on_delete=fields.CASCADE
    )
    
    class Meta:
        table = "_system_tokens"
        schema = "dpo"
