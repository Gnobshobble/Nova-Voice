# Generated by Django 5.0.7 on 2024-08-01 21:09

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_history', '0002_remove_chat_history_message_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='chat_history',
            name='message_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
