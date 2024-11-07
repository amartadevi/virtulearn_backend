# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from PIL import Image
import os

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    image = models.ImageField(upload_to='user_profile/', null=True, blank=True, default='user_profile/default.png')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image and self.image.name != 'user_profile/default.png':
            img_path = self.image.path
            img = Image.open(img_path)

            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(img_path)
