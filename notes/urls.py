from django.urls import path
from .views import NoteListCreateView, NoteDetailView

urlpatterns = [
    path('<int:module_pk>/notes/', NoteListCreateView.as_view(), name='note-list-create'),
    path('<int:module_pk>/notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
]
