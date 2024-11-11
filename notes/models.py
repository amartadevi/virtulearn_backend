from django.db import models
from modules.models import Module
from django.utils import timezone

class Note(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    content = models.TextField()
    topic = models.CharField(max_length=255)
    is_ai_generated = models.BooleanField(default=False)
    is_saved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.topic:
            cleaned_title = self.title.replace('Notes', '').strip()
            self.topic = cleaned_title
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'notes_note'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['topic']),
        ]

    def __str__(self):
        return f"{self.title} ({self.topic})"
