from django.db import models
from modules.models import Module

class Note(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    topic = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title
