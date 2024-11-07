from django.urls import path
from .views import CourseListCreateView, CourseDetailView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', CourseListCreateView.as_view(), name='course-list-create'),
    path('<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)