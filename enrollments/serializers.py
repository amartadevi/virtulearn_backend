from rest_framework import serializers
from .models import EnrollmentRequest
from courses.models import Course
from users.models import User

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    # No need to accept course or student directly from the request
    course_name = serializers.ReadOnlyField(source='course.name')
    student_username = serializers.ReadOnlyField(source='student.username')
    student_image = serializers.ReadOnlyField(source='student.image.url')  # Added user image

    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'course_name', 'status', 'student_username', 'student_image']
        read_only_fields = ['student', 'student_username', 'student_image', 'course_name']

    def create(self, validated_data):
        # The student will be set from the request context
        student = self.context['request'].user
        course = validated_data['course']
        enrollment_request = EnrollmentRequest.objects.create(
            course=course,
            student=student,
            status='approved'  # Assuming status is always 'approved'
        )
        return enrollment_request
