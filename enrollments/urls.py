# enrollments/urls.py
from django.urls import path
from .views import TeacherEnrollmentRequestListView, CreateEnrollmentRequestView, EnrollmentRequestListView

urlpatterns = [
    # Route for teachers to get a list of enrollment requests for their courses
    path('teacher-requests/', TeacherEnrollmentRequestListView.as_view(), name='teacher-enrollment-requests'),
    path('student-requests/', EnrollmentRequestListView.as_view(), name='student-requests'),

    # Route for students to enroll in a course by providing a course code
    path('create/', CreateEnrollmentRequestView.as_view(), name='create-enrollment-request'),
]
