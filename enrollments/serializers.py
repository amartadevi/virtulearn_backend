from rest_framework import serializers
from .models import EnrollmentRequest

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    course_name = serializers.ReadOnlyField(source='course.name')
    student_username = serializers.ReadOnlyField(source='student.username')

    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'course', 'course_name', 'student', 'student_username', 'status']
        read_only_fields = ['student', 'course_name', 'student_username']