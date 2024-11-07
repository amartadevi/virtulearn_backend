from django.contrib import admin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'message', 'response')
    readonly_fields = ('created_at',)
