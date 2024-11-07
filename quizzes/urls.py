from django.urls import path
from .views import QuizListCreateView, QuizDetailView, QuestionListCreateView, QuestionDetailView, StudentAnswerListCreateView,AIQuizGenerateForNoteView,AIQuizGenerateForMultipleNotesView
urlpatterns = [
    path('<int:module_pk>/quizzes/', QuizListCreateView.as_view(), name='quiz-list-create'),
    path('<int:module_pk>/quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('<int:module_pk>/quizzes/<int:quiz_pk>/questions/', QuestionListCreateView.as_view(), name='question-list-create'),
    path('<int:module_pk>/quizzes/<int:quiz_pk>/questions/<int:pk>/', QuestionDetailView.as_view(), name='question-detail'),
    path('<int:module_pk>/quizzes/<int:quiz_pk>/questions/<int:question_pk>/answers/', StudentAnswerListCreateView.as_view(), name='student-answer-list-create'),
    path('<int:module_pk>/notes/<int:note_pk>/generate-quiz/', AIQuizGenerateForNoteView.as_view(), name='generate-quiz-for-note'),
    path('<int:module_pk>/notes/generate-quiz/', AIQuizGenerateForMultipleNotesView.as_view(), name='generate-quiz-for-multiple-notes'),     
]
