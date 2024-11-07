from rest_framework import serializers
from .models import ChatbotMessage

class ChatbotMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatbotMessage
        fields = ['id', 'username', 'message', 'response', 'created_at']
        read_only_fields = ['response', 'created_at'] 