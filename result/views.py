from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import g4f
from .models import QuizResult
from .serializers import QuizResultSerializer
from quizzes.models import Quiz
from notes.models import Note
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

class QuizResultCreateView(generics.CreateAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)

    def create(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, pk=quiz_id)

        data = {
            'quiz': quiz_id,
            'student': request.user.id,
            'score': request.data.get('score', 0),
            'total_questions': request.data.get('total_questions', 0),
            'percentage': request.data.get('percentage', 0.0),
            'student_answers': request.data.get('student_answers', {})
        }

        try:
            # Check for existing result
            result = QuizResult.objects.filter(
                student=request.user,
                quiz=quiz
            ).first()

            if result:
                serializer = self.get_serializer(result, data=data)
            else:
                serializer = self.get_serializer(data=data)

            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            response_data = serializer.data
            
            # Generate suggestions for low scores
            if float(data['percentage']) < 80:
                suggestions = self.generate_suggestions(
                    quiz=quiz,
                    student_answers=data['student_answers']
                )
                response_data['suggestions'] = suggestions

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def generate_suggestions(self, quiz, student_answers):
        try:
            # Get related notes
            notes = Note.objects.filter(id__in=quiz.note_ids)
            notes_content = " ".join([note.content for note in notes])
            
            # Analyze incorrect answers
            incorrect_topics = []
            for answer in student_answers.values():
                if not answer.get('is_correct', False):
                    incorrect_topics.append(answer.get('question', ''))

            # Generate AI suggestions using g4f
            prompt = f"""
            Based on the student's performance in a quiz about {quiz.title}, 
            they struggled with the following topics:
            {', '.join(incorrect_topics)}

            The learning material covered:
            {notes_content[:500]}  # Limiting content length

            Please provide:
            1. Specific study suggestions
            2. Key concepts to review
            3. 2-3 relevant YouTube tutorial links
            4. Additional practice exercises
            Format the response in JSON.
            """

            response = g4f.ChatCompletion.create(
                model=g4f.models.gpt_35_turbo,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )

            return response

        except Exception as e:
            return {
                "error": f"Failed to generate suggestions: {str(e)}",
                "general_suggestions": [
                    "Review the course materials",
                    "Practice with similar questions",
                    "Consult with your teacher"
                ]
            }

class StudentQuizResultView(generics.RetrieveAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get('quiz_id')
        user = self.request.user
        
        # Only return results for quizzes that the student has attempted
        if not QuizResult.objects.filter(quiz_id=quiz_id, student=user).exists():
            return Response(None, status=status.HTTP_404_NOT_FOUND)
            
        try:
            quiz_result = QuizResult.objects.get(
                quiz_id=quiz_id,
                student=user
            )
            serializer = self.get_serializer(quiz_result)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except QuizResult.DoesNotExist:
            return Response(None, status=status.HTTP_404_NOT_FOUND)

class TeacherQuizResultsView(generics.ListAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not (self.request.user.role == 'teacher' or self.request.user.is_staff):
            return QuizResult.objects.none()
        return QuizResult.objects.filter(
            quiz_id=self.kwargs.get('quiz_id')
        ).select_related('student').order_by('-percentage')

class QuizResultReviewView(generics.RetrieveAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        quiz_id = self.kwargs.get('quiz_id')
        student_id = self.kwargs.get('student_id')
        
        logger.debug(f"Fetching review - Quiz ID: {quiz_id}, Student ID: {student_id}")
        
        # Get the quiz result
        quiz_result = get_object_or_404(
            QuizResult,
            quiz_id=quiz_id,
            student_id=student_id
        )
        
        # Debug log the raw student_answers
        logger.debug(f"Raw student_answers from DB: {quiz_result.student_answers}")
        
        # Check if user is the student who took the quiz or a teacher
        user = self.request.user
        if not (user.id == student_id or 
                user.role == 'teacher' or 
                user.is_staff):
            raise PermissionDenied(
                "You don't have permission to view this review"
            )
            
        return quiz_result

    def retrieve(self, request, *args, **kwargs):
        try:
            quiz_result = self.get_object()
            serializer = self.get_serializer(quiz_result)
            data = serializer.data
            
            logger.debug(f"Serialized data before response: {data}")
            return Response(data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error retrieving quiz review: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class StudentQuizResultsView(generics.ListAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Get only the attempted quizzes for this student
        return QuizResult.objects.filter(
            student=user
        ).select_related('quiz').order_by('-completed_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        # Format the response with quiz details
        results = []
        for result in serializer.data:
            quiz_data = {
                'quiz_id': result['quiz'],
                'quiz_title': result['quiz_title'],
                'score': result['score'],
                'total_questions': result['total_questions'],
                'percentage': result['percentage'],
                'completed_at': result['completed_at'],
                'student_answers': result['student_answers']
            }
            results.append(quiz_data)
        
        return Response(results, status=status.HTTP_200_OK)