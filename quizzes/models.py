from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from modules.models import Module
from notes.models import Note
from django.utils import timezone
from django.core.exceptions import PermissionDenied

class Quiz(models.Model):
    ASSIGNMENT = 'assignment'
    PRACTICE = 'practice'
    GRADED = 'graded'
    QUIZ_TYPES = [
        (ASSIGNMENT, 'Assignment'),
        (PRACTICE, 'Practice Quiz'),
        (GRADED, 'Graded Quiz')
    ]

    QNA = 'QNA'
    MCQ = 'MCQ'
    CATEGORY_TYPES = [
        (QNA, 'Question and Answer'),
        (MCQ, 'Multiple Choice Question')
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    description = models.TextField(default='no description given')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES, default=PRACTICE)
    category = models.CharField(max_length=10, choices=CATEGORY_TYPES, default=MCQ)
    created_at = models.DateTimeField(auto_now_add=True)
    quiz_duration = models.PositiveIntegerField(help_text="Duration of the quiz in minutes", default=15)  # Storing duration in minutes
    note = models.TextField(default="No notes available")
    content = models.TextField(default='no content given')
    is_ai_generated = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.created_by.role == 'student':
            raise ValidationError("Students cannot create quizzes.")
        if self.module.course.created_by != self.created_by:
            raise PermissionDenied("Only the course creator can create quizzes.")
        super().save(*args, **kwargs)

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    options = models.JSONField(default=list)
    correct_answer = models.CharField(max_length=255, default='')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.question_text

    def save(self, *args, **kwargs):
        if self.quiz.category == 'MCQ' and not all([self.options, self.correct_answer]):
            raise ValidationError("All options and a correct answer must be provided for MCQ.")
        super().save(*args, **kwargs)

# Renamed related_name to 'quiz_results'
class Result(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='quiz_results')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_quiz_results')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    date_taken = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.student.username} - {self.quiz.title} - {self.score}'

class StudentAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, blank=True, null=True)  # Only applicable for MCQ
    answer_text = models.TextField(blank=True, null=True)  # Only applicable for QNA

    def __str__(self):
        return f'{self.student.username} - {self.question.quiz.title} - {self.question.question_text}'

