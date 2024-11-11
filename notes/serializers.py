from rest_framework import serializers
from .models import Note

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'id', 
            'module', 
            'title', 
            'content', 
            'topic',
            'is_ai_generated',
            'is_saved',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'module', 'created_at', 'updated_at']
