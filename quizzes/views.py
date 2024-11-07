from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, PermissionDenied
import logging
from .models import Quiz, Question, StudentAnswer
from .serializers import QuizSerializer, QuestionSerializer, StudentAnswerSerializer
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)

class QuizListCreateView(generics.ListCreateAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Quiz.objects.filter(module_id=self.kwargs['module_pk'])

    def perform_create(self, serializer):
        if self.request.user.role == 'student':
            raise PermissionDenied("Students cannot create quizzes.")
        
        module_id = self.kwargs.get('module_pk')
        quiz = serializer.save(
            created_by=self.request.user,
            module_id=module_id,
        )
        return quiz

class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        logger.debug(f"Fetching quiz for module {self.kwargs['module_pk']} , Quiz ID: {self.kwargs['pk']}")
        return Quiz.objects.filter(module_id=self.kwargs['module_pk'], id=self.kwargs['pk'])
    
    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.first()
        if obj is None:
            raise NotFound(f"Quiz not found for module {self.kwargs.get('module_pk')}")
        return obj

class QuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        quiz = self.get_quiz()
        return Question.objects.filter(quiz=quiz)

    def get_quiz(self):
        try:
            return Quiz.objects.get(pk=self.kwargs['quiz_pk'], module_id=self.kwargs['module_pk'])
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found.")

    def perform_create(self, serializer):
        quiz = self.get_quiz()
        serializer.save(quiz=quiz)

class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Question.objects.filter(quiz__module_id=self.kwargs['module_pk'])

class StudentAnswerListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        question = self.get_question()
        return StudentAnswer.objects.filter(question=question, student=self.request.user)

    def get_question(self):
        try:
            return Question.objects.get(pk=self.kwargs['question_pk'], quiz__module_id=self.kwargs['module_pk'])
        except Question.DoesNotExist:
            raise NotFound("Question not found.")

    def perform_create(self, serializer):
        question = self.get_question()
        serializer.save(question=question, student=self.request.user)
        

from rest_framework import status, generics
from rest_framework.response import Response
from modules.models import Module
from .models import Note, Quiz
from .serializers import QuizSerializer
from .ai_quiz_model import AIQuizManager

class AIQuizGenerateForNoteView(generics.CreateAPIView):
    serializer_class = QuizSerializer

    def post(self, request, module_pk, note_pk):
        try:
            note = Note.objects.get(pk=note_pk, module_id=module_pk)
            ai_quiz_manager = AIQuizManager()
            quiz_content = ai_quiz_manager.generate_quiz(note.content)

            # Return the generated content without saving
            return Response({
                'title': f"Quiz for {note.title}",
                'quiz_content': quiz_content,  # Send the actual quiz content
                'message': 'Quiz generated successfully'
            }, status=status.HTTP_201_CREATED)

        except Note.DoesNotExist:
            return Response({"error": "Note not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AIQuizGenerateForMultipleNotesView(generics.CreateAPIView):
    serializer_class = QuizSerializer

    def post(self, request, module_pk):
        note_ids = request.data.get("note_ids")  # Expecting a list of note IDs

        if not note_ids:
            return Response({"error": "No note IDs provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            notes = Note.objects.filter(id__in=note_ids, module_id=module_pk)

            if not notes.exists():
                return Response({"error": "No valid notes found."}, status=status.HTTP_404_NOT_FOUND)

            # Initialize the AI quiz manager
            ai_quiz_manager = AIQuizManager()

            # Combine contents of the notes
            combined_content = " ".join([note.content for note in notes])

            # Generate quiz based on the combined content of the notes
            quiz_content = ai_quiz_manager.generate_quiz(combined_content)

            # Create a new quiz for multiple notes
            quiz = Quiz.objects.create(
                module_id=module_pk,
                title=f"Quiz for Module {module_pk}",
                content=quiz_content,
                created_by=request.user,
                note="Multiple notes"  # Indicating multiple notes used
            )

            return Response({"message": "Quiz for selected notes generated successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

