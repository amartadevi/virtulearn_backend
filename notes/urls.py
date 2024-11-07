from django.urls import path
from .views import (
    NoteListCreateView, 
    NoteDetailView, 
    AINoteGenerateView, 
    NoteRegenerateView
)

urlpatterns = [
    path('<int:module_pk>/notes/', NoteListCreateView.as_view(), name='note-list-create'),
    path('<int:module_pk>/notes/<int:pk>/', NoteDetailView.as_view(), name='note-detail'),
    # Update this line to match the frontend request
    path('<int:module_pk>/generate-notes/', AINoteGenerateView.as_view(), name='generate-notes'),
    path('<int:module_pk>/notes/<int:note_id>/regenerate/', NoteRegenerateView.as_view(), name='note-regenerate'),
]
