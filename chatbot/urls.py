from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_response, name='chatbot-response'),
    path('history/', views.get_chatbot_history, name='chatbot-history'),
    path('clear/', views.clear_chatbot_history, name='clear-chatbot-history'),
]
