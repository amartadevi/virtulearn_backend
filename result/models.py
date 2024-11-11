from django.db import models
from django.contrib.auth import get_user_model
from quizzes.models import Quiz
from decimal import Decimal

class QuizResult(models.Model):
    student = models.ForeignKey(
        get_user_model(), 
        on_delete=models.CASCADE,
        related_name='quiz_results'
    )
    quiz = models.ForeignKey(
        Quiz, 
        on_delete=models.CASCADE,
        related_name='results'
    )
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True,
        blank=True
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    student_answers = models.JSONField(default=dict)

    class Meta:
        db_table = 'result_quizresult'
        unique_together = ['student', 'quiz']
        ordering = ['-completed_at']

    def save(self, *args, **kwargs):
        if self.total_questions > 0:
            self.percentage = Decimal(str((self.score / self.total_questions) * 100))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username}'s result for {self.quiz.title}"