# enrollments/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import EnrollmentRequest
from .serializers import EnrollmentRequestSerializer
from rest_framework.permissions import IsAuthenticated

class StudentEnrollmentRequestListView(generics.ListAPIView):
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print("Fetching student enrollment requests for user:", self.request.user)
        return EnrollmentRequest.objects.filter(student=self.request.user)

class TeacherEnrollmentRequestListView(generics.ListAPIView):
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        print("Fetching teacher enrollment requests for user:", self.request.user)
        return EnrollmentRequest.objects.filter(course__created_by=self.request.user)

class CreateEnrollmentRequestView(generics.CreateAPIView):
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        print("Creating enrollment request for user:", self.request.user)
        serializer.save(student=self.request.user)

class EnrollmentRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EnrollmentRequest.objects.all()
    serializer_class = EnrollmentRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        enrollment_request = self.get_object()
        print("Updating enrollment request:", enrollment_request)
        if request.user.role not in ['admin', 'teacher'] or enrollment_request.course.created_by != request.user:
            return Response({"detail": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
        enrollment_request.status = request.data.get('status', enrollment_request.status)
        enrollment_request.save()
        if enrollment_request.status == 'approved':
            enrollment_request.course.students.add(enrollment_request.student)
        return Response({"detail": "Enrollment request updated successfully."}, status=status.HTTP_200_OK)