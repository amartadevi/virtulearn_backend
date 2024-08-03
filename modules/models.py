from django.db import models
from courses.models import Course

class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.title
