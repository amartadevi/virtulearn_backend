from rest_framework import serializers
from .models import Note

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'module', 'title', 'content', 'topic']
        read_only_fields = ['id', 'module']
