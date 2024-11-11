from django.urls import path
from . import views

app_name = 'result'

urlpatterns = [
    # Match frontend URL: baseUrl + 'result/$quizId/submit-result/'
    path('<int:quiz_id>/submit-result/', 
         views.QuizResultCreateView.as_view(), 
         name='submit-quiz-result'),
    
    # Match frontend URL: baseUrl + 'result/${quiz.id}/my-result/'
    path('<int:quiz_id>/my-result/', 
         views.StudentQuizResultView.as_view(), 
         name='student-quiz-result'),
    
    # Match frontend URL: baseUrl + 'result/$quizId/results/'
    path('<int:quiz_id>/results/', 
         views.TeacherQuizResultsView.as_view(), 
         name='quiz-results-list'),
    
    # Match frontend URL: baseUrl + 'result/$quizId/student/$studentId/review/'
    path('<int:quiz_id>/student/<int:student_id>/review/', 
         views.QuizResultReviewView.as_view(), 
         name='quiz-result-review'),
    
    # New endpoint for getting all attempted quizzes
    path('my-results/', 
         views.StudentQuizResultsView.as_view(), 
         name='student-quiz-results'),
    path('<int:quiz_id>/student/<int:student_id>/suggestions/',
         views.QuizSuggestionsView.as_view(),
         name='quiz-suggestions'),
]