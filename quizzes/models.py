from django.db import models
from modules.models import Module

class Quiz(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    questions = models.TextField()

    def __str__(self):
        return self.title
