from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('users.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/enrollment-requests/', include('enrollments.urls')),
    path('api/modules/', include('modules.urls')),
    path('api/quizzes/', include('quizzes.urls')),
    path('api/discussions/', include('discussions.urls')),
    path('api/chat/', include('chat.urls')),
]