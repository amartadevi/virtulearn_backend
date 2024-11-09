from django.urls import path
from .views import ResultListCreateView, ResultDetailView

urlpatterns = [
    path('modules/<int:module_pk>/quizzes/<int:quiz_pk>/results/', ResultListCreateView.as_view(), name='result-list-create'),
    path('modules/<int:module_pk>/quizzes/<int:quiz_pk>/results/<int:pk>/', ResultDetailView.as_view(), name='result-detail'),
]
