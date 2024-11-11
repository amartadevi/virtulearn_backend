from rest_framework import serializers
from .models import QuizResult
import logging

logger = logging.getLogger(__name__)

class QuizResultSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    suggestions = serializers.JSONField(required=False)

    class Meta:
        model = QuizResult
        fields = [
            'id', 'student', 'quiz', 'score', 
            'total_questions', 'percentage', 
            'completed_at', 'student_answers',
            'student_name', 'suggestions'
        ]
        read_only_fields = ['id', 'completed_at']

    def get_student_name(self, obj):
        return obj.student.username if obj.student else "Unknown Student"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Ensure student_answers is properly formatted
        formatted_answers = {}
        if instance.student_answers:
            try:
                # Handle if student_answers is a list
                if isinstance(instance.student_answers, list):
                    for idx, answer in enumerate(instance.student_answers):
                        if isinstance(answer, dict):
                            formatted_answers[str(idx)] = {
                                'question': answer.get('question', ''),
                                'selected_answer': answer.get('selected_answer', ''),
                                'correct_answer': answer.get('correct_answer', ''),
                                'is_correct': answer.get('is_correct', False),
                            }
                # Handle if student_answers is already a dict
                elif isinstance(instance.student_answers, dict):
                    for key, value in instance.student_answers.items():
                        if isinstance(value, dict):
                            formatted_answers[str(key)] = {
                                'question': value.get('question', ''),
                                'selected_answer': value.get('selected_answer', ''),
                                'correct_answer': value.get('correct_answer', ''),
                                'is_correct': value.get('is_correct', False),
                            }
            except Exception as e:
                logger.error(f"Error formatting student answers: {e}")
                formatted_answers = {}
                
        data['student_answers'] = formatted_answers
        return data

    def validate(self, data):
        if data['total_questions'] <= 0:
            raise serializers.ValidationError(
                "Total questions must be greater than 0"
            )
        if data['score'] > data['total_questions']:
            raise serializers.ValidationError(
                "Score cannot be greater than total questions"
            )
        return data