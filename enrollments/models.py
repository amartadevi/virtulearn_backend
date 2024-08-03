from django.db import models
from courses.models import Course
from users.models import User

class EnrollmentRequest(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollment_requests')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollment_requests')
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')], default='pending')

    def _str_(self):
        return f'{self.student.username} - {self.course.name} ({self.status})'