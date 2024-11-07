from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/users/', include('users.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/enrollments/', include('enrollments.urls')),
    path('api/modules/', include('modules.urls')),  # Include notes URLs in modules.urls
    path('api/quizzes/', include('quizzes.urls')),
    path('api/discussions/', include('discussions.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/chatbot/', include('chatbot.urls')),
    path('api/results/', include('results.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
