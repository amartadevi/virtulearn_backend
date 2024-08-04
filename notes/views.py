from rest_framework import generics
from .models import Note
from .serializers import NoteSerializer

class NoteListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteSerializer

    def get_queryset(self):
        module_pk = self.kwargs['module_pk']
        return Note.objects.filter(module_id=module_pk)

    def perform_create(self, serializer):
        module_pk = self.kwargs['module_pk']
        serializer.save(module_id=module_pk)

class NoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NoteSerializer

    def get_queryset(self):
        module_pk = self.kwargs['module_pk']
        return Note.objects.filter(module_id=module_pk)
