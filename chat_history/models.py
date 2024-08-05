from django.db import models
import uuid
from django.contrib import admin
# Create your models here.
class Chat_History(models.Model):
    user_id = models.BigIntegerField()
    chat_id = models.BigIntegerField()
    messages = models.CharField(max_length=500000)
    message_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    message_index = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.user_id)
