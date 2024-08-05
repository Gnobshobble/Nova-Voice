from django.contrib import admin
from .models import Chat_History

# Register your models here.

@admin.register(Chat_History)
class Chat_HistoryAdmin(admin.ModelAdmin):
    list_display = ("user_id", "chat_id", "messages", "message_id", "message_index")