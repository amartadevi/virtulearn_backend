from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound, PermissionDenied
import logging
from .models import Quiz, Question, StudentAnswer
from .serializers import QuizSerializer, QuestionSerializer, StudentAnswerSerializer
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Quiz
from result.models import QuizResult
from .models import Note
from notes.serializers import NoteSerializer
from django.shortcuts import get_object_or_404
from modules.models import Module

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
        note_ids = request.data.get("note_ids", [])
        
        if not note_ids:
            return Response(
                {"error": "No note IDs provided."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Convert note_ids to list if it's not already
            if isinstance(note_ids, str):
                note_ids = [int(id.strip()) for id in note_ids.split(',') if id.strip()]
            elif isinstance(note_ids, int):
                note_ids = [note_ids]
            
            notes = Note.objects.filter(id__in=note_ids, module_id=module_pk)

            if not notes.exists():
                return Response(
                    {"error": "No valid notes found."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            note_titles = [note.title for note in notes]
            combined_content = " ".join([note.content for note in notes])
            
            ai_quiz_manager = AIQuizManager()
            quiz_content = ai_quiz_manager.generate_quiz(combined_content)
            quiz_title = f"Quiz on: {', '.join(note_titles)}"

            # Store note IDs as a list
            note_ids_list = [note.id for note in notes]

            return Response({
                "title": quiz_title,
                "content": quiz_content,
                "quiz_content": quiz_content,
                "note_ids": note_ids_list,  # Send as a list
                "note_titles": note_titles,
                "is_ai_generated": True,
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class GeneratedQuizRetrieveView(generics.RetrieveAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, module_pk):
        try:
            # Get note_ids from query params
            note_ids_str = request.GET.get('note_ids', '')
            if not note_ids_str:
                return Response(
                    {"error": "note_ids parameter is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get the latest generated quiz for these notes
            quiz = Quiz.objects.filter(
                module_id=module_pk,
                is_ai_generated=True,
            ).latest('created_at')

            if not quiz:
                return Response(
                    {"error": "No generated quiz found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({
                'title': quiz.title,
                'content': quiz.content,
                'quiz_content': quiz.content,  # For compatibility
                'note_ids': note_ids_str,
                'is_ai_generated': True,
            })

        except Quiz.DoesNotExist:
            return Response(
                {"error": "No generated quiz found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_quiz_result(request, quiz_id):
    try:
        quiz = Quiz.objects.get(id=quiz_id)
        data = request.data
        
        # Create quiz result
        result = QuizResult.objects.create(
            quiz=quiz,
            student=request.user,
            score=int(data.get('score', 0)),
            total_questions=int(data.get('total_questions', 0)),
            percentage=float(data.get('percentage', 0)),
            student_answers=data.get('student_answers', {})
        )

        return Response({
            'message': 'Quiz result submitted successfully',
            'result_id': result.id
        }, status=201)
    
    except Quiz.DoesNotExist:
        return Response({'error': 'Quiz not found'}, status=404)
    except Exception as e:
        print(f"Error in submit_quiz_result: {str(e)}")
        return Response({'error': str(e)}, status=400)

class QuizRelatedNotesView(generics.ListAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        try:
            quiz_id = self.kwargs.get('quiz_id')
            quiz = get_object_or_404(Quiz, pk=quiz_id)
            
            # Get all notes from the same module
            module_notes = Note.objects.filter(module=quiz.module)
            
            # Log for debugging
            logger.debug(f"Found {module_notes.count()} notes for quiz {quiz_id}")
            
            return module_notes

        except Quiz.DoesNotExist:
            logger.error(f"Quiz {quiz_id} not found")
            return Note.objects.none()
        except Exception as e:
            logger.error(f"Error in QuizRelatedNotesView: {e}")
            return Note.objects.none()

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'success',
                'notes': serializer.data
            })
        except Exception as e:
            logger.error(f"Error listing related notes: {e}")
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class QuizCreateView(generics.CreateAPIView):
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        module_id = self.kwargs.get('module_pk')
        module = get_object_or_404(Module, pk=module_id)
        
        # Get the note ID from the request data
        note_id = self.request.data.get('note_id')
        
        # Save the quiz with the note ID
        serializer.save(
            module=module,
            note_ids=[note_id] if note_id else []
        )

class QuizSuggestionsView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            quiz_id = self.kwargs.get('quiz_id')
            student_id = self.kwargs.get('student_id')
            
            result = QuizResult.objects.get(
                quiz_id=quiz_id,
                student_id=student_id
            )
            
            quiz = result.quiz
            
            # Get the specific notes linked to this quiz
            note_ids = quiz.get_note_ids()
            quiz_notes = Note.objects.filter(id__in=note_ids) if note_ids else []
            
            logger.debug(f"Quiz ID: {quiz_id}")
            logger.debug(f"Found {len(quiz_notes)} notes for this quiz")

            if result.percentage >= 80:
                return Response({
                    "performance_message": "Excellent work! Keep it up!"
                })

            suggestions = {
                "study_suggestions": [
                    f"Review the material for {quiz.title}",
                    "Practice similar questions in this topic",
                    "Focus on understanding core concepts"
                ],
                "key_concepts": [
                    "Review the following concepts:",
                    *[answer.get('question', '') for answer in result.student_answers.values() 
                      if not answer.get('is_correct', False)][:3]
                ],
                "practice_exercises": [
                    "Create practice questions on this topic",
                    "Review and understand incorrect answers",
                    "Try solving similar problems"
                ],
                "related_notes": [
                    {
                        "id": note.id,
                        "title": note.title,
                        "module_id": note.module.id,
                        "topic": note.topic,
                        "content_preview": note.content[:100] + "..." if note.content else ""
                    } for note in quiz_notes
                ]
            }

            return Response(suggestions)

        except Exception as e:
            logger.error(f"Error in QuizSuggestionsView: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )