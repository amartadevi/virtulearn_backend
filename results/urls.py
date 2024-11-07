from django.urls import path
from .views import ResultListCreateView, ResultDetailView,SubmitQuizResult

urlpatterns = [
    path('<int:module_pk>/quizzes/<int:quiz_pk>/results/', ResultListCreateView.as_view(), name='result-list-create'),
    path('<int:module_pk>/quizzes/<int:quiz_pk>/results/<int:pk>/', ResultDetailView.as_view(), name='result-detail'),
    path('<int:quiz_pk>/submit-quiz/', SubmitQuizResult.as_view(), name='submit-quiz'),
]
