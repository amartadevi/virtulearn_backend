from django.db import models
from django.conf import settings
from quizzes.models import Quiz
from django.utils import timezone

# Renamed related_name to 'quiz_result_set'
class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_result_set')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_result_set')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date_taken = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.student.username} - {self.quiz.title} - {self.score}'
    
from django.db import models
from django.conf import settings
from .models import Quiz

class QuizResult(models.Model):
    quiz_id = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    answers = models.JSONField()

    def __str__(self):
        return f'QuizResult:{self.student} - {self.quiz_id} - {self.score}'

