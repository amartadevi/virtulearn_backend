from modules.models import Module
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .ai_notes_model import AINotesManager
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

class AINoteGenerateView(generics.CreateAPIView):
    serializer_class = NoteSerializer

    def post(self, request, module_pk):
        try:
            module = Module.objects.get(pk=module_pk)
            topic = request.data.get('topic', '')
            
            print(f"Received request to generate notes for topic: {topic}")

            if not topic:
                return Response(
                    {"detail": "Topic must be provided."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                # Use AINotesManager to generate the notes
                ai_manager = AINotesManager()
                notes_content = ai_manager.generate_notes(topic)
                
                if not notes_content:
                    raise ValueError("Generated content is empty")

                # Return the generated content without saving
                response_data = {
                    'title': f"{topic} Notes",
                    'content': notes_content,
                    'topic': topic
                }
                
                print(f"Generated response: {response_data}")
                return Response(response_data, status=status.HTTP_200_OK)
                
            except Exception as ai_error:
                print(f"AI Generation error: {ai_error}")
                return Response(
                    {"detail": f"Failed to generate AI content: {str(ai_error)}"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        except Module.DoesNotExist:
            return Response(
                {"detail": "Module not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(f"Error generating notes: {e}")
            return Response(
                {"detail": f"Error generating notes: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class NoteRegenerateView(generics.UpdateAPIView):
    serializer_class = NoteSerializer

    def post(self, request, module_pk, note_id):
        try:
            note = Note.objects.get(id=note_id, module_id=module_pk)
            topic = note.topic  # Fix: Get the topic from note object
            
            if not topic:
                return Response(
                    {"detail": "Note has no topic to regenerate from."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Note.DoesNotExist:
            return Response(
                {"detail": "Note not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Generate new content using the original topic
        ai_manager = AINotesManager()
        notes_content = ai_manager.generate_notes(topic)

        # Update the note's content
        note.content = notes_content
        note.save()

        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_200_OK)
