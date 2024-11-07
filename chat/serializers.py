from rest_framework import serializers
from .models import ChatMessage

class ChatMessageSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'username', 'message', 'response', 'created_at']
        read_only_fields = ['response', 'created_at']
