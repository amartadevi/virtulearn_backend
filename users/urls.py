from django.urls import path
from .views import UserRegistrationView, UserProfileView, CurrentUserView ,LoginView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('user/', CurrentUserView.as_view(), name='user-detail'),  # This should handle the /api/user/ endpoint
    path('login/', LoginView.as_view(), name='login'),
]