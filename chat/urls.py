from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat_response, name='chat-response'),
    path('chat/history/', views.get_chat_history, name='chat-history'),
    path('chat/clear/', views.clear_chat_history, name='clear-chat-history'),
]
