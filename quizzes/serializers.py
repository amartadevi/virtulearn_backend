from rest_framework import serializers
from .models import Quiz, Question, Result, StudentAnswer

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'options', 'correct_answer']

class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'content', 'module', 
                 'quiz_type', 'category', 'is_ai_generated', 'questions']
        read_only_fields = ['created_by']

    def create(self, validated_data):
        questions_data = validated_data.pop('questions', [])
        quiz = Quiz.objects.create(**validated_data)
        
        for question_data in questions_data:
            Question.objects.create(quiz=quiz, **question_data)
        
        return quiz

    def validate_quiz_type(self, value):
        if value not in ['assignment', 'practice', 'graded']:
            raise serializers.ValidationError(f"{value} is not a valid choice for quiz_type.")
        return value

    def validate_category(self, value):
        if value not in ['QNA', 'MCQ']:
            raise serializers.ValidationError(f"{value} is not a valid choice for category.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['questions'] = QuestionSerializer(instance.questions.all(), many=True).data
        return representation

# Adjust the related name in the ResultSerializer
class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'quiz', 'student', 'score', 'date_taken']

class StudentAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['id', 'question', 'student', 'selected_option', 'answer_text']
