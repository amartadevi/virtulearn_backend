from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import EnrollmentRequest, Course
from .serializers import EnrollmentRequestSerializer
from courses.serializers import CourseSerializer

class TeacherEnrollmentRequestListView(generics.ListAPIView):
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return the list of enrollment requests for the courses created by the teacher.
        """
        teacher = self.request.user
        print(f"Fetching enrollment requests for teacher: {teacher.username}")

        # Filter enrollment requests for courses created by the teacher
        return EnrollmentRequest.objects.filter(course__created_by=teacher)


class CreateEnrollmentRequestView(generics.CreateAPIView):
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        student = self.request.user
        course_id = self.request.data.get('course_id')
        course_code = self.request.data.get('course_code')

        print(f"Received course_id: {course_id}, course_code: {course_code} from student: {student.username}")

        # Check if course_id or course_code is missing
        if not course_id or not course_code:
            print("Error: course_id or course_code is missing from the request.")
            return Response({"detail": "Course ID or Course Code is missing."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the course ID and course code
        try:
            course = Course.objects.get(id=course_id, code=course_code)
            print(f"Course found: {course.name} for course ID: {course_id} and course code: {course_code}")
        except Course.DoesNotExist:
            print(f"Error: Course with ID: {course_id} and course code: {course_code} does not exist.")
            return Response({"detail": "Invalid course ID or course code."}, status=status.HTTP_400_BAD_REQUEST)

        # Automatically enroll the student in the course
        course.students.add(student)
        print(f"Student {student.username} successfully enrolled in course {course.name}")

        # Optionally, create an enrollment request for tracking purposes
        serializer.save(student=student, course=course, status='approved')

        return Response({"detail": "You have been successfully enrolled in the course."}, status=status.HTTP_200_OK)




class EnrollmentRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Filter enrollment requests for the logged-in student
        user = request.user
        print(f"Fetching enrollment requests for user: {user.username}")

        if user.role != 'student':
            print(f"Unauthorized access attempt by user: {user.username}")
            return Response({"detail": "Only students can access enrollment requests."}, status=status.HTTP_403_FORBIDDEN)

        # Get all enrollment requests made by the student
        enrollment_requests = EnrollmentRequest.objects.filter(student=user)
        print(f"Found {enrollment_requests.count()} enrollment requests for student: {user.username}")

        # Include course details in the response
        enrollment_data = []
        for enrollment in enrollment_requests:
            course = enrollment.course
            print(f"Processing course {course.name} for enrollment status {enrollment.status}")
            enrollment_info = {
                "course_name": course.name,
                "course_description": course.description,
                "course_image": course.image.url if course.image else None,
                "enrollment_status": enrollment.status,
            }
            enrollment_data.append(enrollment_info)

        return Response(enrollment_data, status=status.HTTP_200_OK)
