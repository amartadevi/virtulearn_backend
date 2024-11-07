from rest_framework import serializers
from .models import Result

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'quiz', 'student', 'score', 'date_taken']
        read_only_fields = ['quiz', 'student', 'score']

    def create(self, validated_data):
        return Result.objects.create(**validated_data)
    
from rest_framework import serializers
from .models import QuizResult

class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = ['quiz_id', 'student', 'score', 'answers']