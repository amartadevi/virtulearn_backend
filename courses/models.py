# courses/models.py
from django.db import models
from users.models import User
import random
import string
from PIL import Image

class Course(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses')
    students = models.ManyToManyField(User, related_name='enrolled_courses', blank=True)
    image = models.ImageField(upload_to='course_images/', null=True, blank=True, default='course_images/default.png')

    class Meta:
        unique_together = ('name', 'description')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

        if self.image and self.image.name != 'course_images/default.png':
            img_path = self.image.path
            img = Image.open(img_path)

            if img.height > 600 or img.width > 800:
                output_size = (600, 800)
                img.thumbnail(output_size)
                img.save(img_path)

    def generate_unique_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
