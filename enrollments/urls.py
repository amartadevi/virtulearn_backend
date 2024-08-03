# enrollments/urls.py
from django.urls import path
from .views import (
    StudentEnrollmentRequestListView,
    TeacherEnrollmentRequestListView,
    CreateEnrollmentRequestView,
    EnrollmentRequestDetailView
)

urlpatterns = [
    path('student-requests/', StudentEnrollmentRequestListView.as_view(), name='student-enrollment-requests'),
    path('teacher-requests/', TeacherEnrollmentRequestListView.as_view(), name='teacher-enrollment-requests'),
    path('create/', CreateEnrollmentRequestView.as_view(), name='create-enrollment-request'),
    path('<int:pk>/', EnrollmentRequestDetailView.as_view(), name='enrollment-request-detail'),
]