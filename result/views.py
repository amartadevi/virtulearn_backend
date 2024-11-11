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
import json

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
                # Get related notes content
                notes = Note.objects.filter(id__in=quiz.note_ids)
                notes_content = " ".join([note.content for note in notes])
                
                # Get incorrect answers for topics
                incorrect_topics = []
                for answer in data['student_answers'].values():
                    if not answer.get('is_correct', False):
                        incorrect_topics.append(answer.get('question', ''))

                # Generate AI suggestions
                prompt = f"""
                As an AI tutor, analyze the student's quiz performance and provide personalized learning suggestions.
                
                Quiz Title: {quiz.title}
                Score: {data['percentage']}%
                Topics they struggled with: {', '.join(incorrect_topics)}
                
                Related learning material:
                {notes_content[:1000]}  # Limiting content length for prompt
                
                Please provide:
                1. 3-4 specific study suggestions based on their mistakes
                2. 3-4 key concepts they should review
                3. 2-3 relevant YouTube tutorial links (real, working links)
                4. 2-3 practice exercises they should try
                
                Format the response in JSON with this structure:
                {{
                    "study_suggestions": ["suggestion1", "suggestion2", "suggestion3"],
                    "key_concepts": ["concept1", "concept2", "concept3"],
                    "youtube_links": ["link1", "link2"],
                    "practice_exercises": ["exercise1", "exercise2"]
                }}
                
                Make suggestions specific to their weak areas and the actual course content.
                """

                try:
                    ai_response = g4f.ChatCompletion.create(
                        model=g4f.models.gpt_35_turbo,
                        messages=[{"role": "user", "content": prompt}],
                        stream=False
                    )
                    
                    suggestions = json.loads(ai_response)
                    
                    # Add suggestions to response
                    response_data['suggestions'] = {
                        "study_suggestions": suggestions.get("study_suggestions", [])[:4],
                        "key_concepts": suggestions.get("key_concepts", [])[:4],
                        "youtube_links": suggestions.get("youtube_links", [])[:3],
                        "practice_exercises": suggestions.get("practice_exercises", [])[:3]
                    }
                except Exception as e:
                    logger.error(f"Error generating AI suggestions: {e}")
                    response_data['suggestions'] = {
                        "study_suggestions": ["Review the course materials"],
                        "key_concepts": ["Focus on areas where you made mistakes"],
                        "youtube_links": [],
                        "practice_exercises": ["Practice similar questions"]
                    }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class StudentQuizResultView(generics.RetrieveAPIView):
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        quiz_id = self.kwargs.get('quiz_id')
        try:
            result = QuizResult.objects.get(
                quiz_id=quiz_id,
                student=request.user
            )
            serializer = self.get_serializer(result)
            return Response(serializer.data)
        except QuizResult.DoesNotExist:
            # Return a more graceful response for non-attempted quizzes
            return Response(
                {
                    'quiz_id': quiz_id,
                    'message': 'Quiz not attempted yet',
                    'attempted': False
                },
                status=status.HTTP_200_OK  # Changed from 404 to 200
            )

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
        return QuizResult.objects.filter(
            student=user
        ).select_related('quiz').order_by('-completed_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Check if there are any results
        if not queryset.exists():
            return Response([], status=status.HTTP_200_OK)  # Return empty list instead of 404
            
        serializer = self.get_serializer(queryset, many=True)
        
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
            
            # Extract multiple topics from quiz title
            quiz_title = quiz.title.lower()
            if 'quiz on:' in quiz_title:
                topics_part = quiz_title.split('quiz on:')[-1]
            elif 'quiz for' in quiz_title:
                topics_part = quiz_title.split('quiz for')[-1]
            else:
                topics_part = quiz_title

            # Split topics by comma or 'and' and clean them
            topics = [
                topic.replace('notes', '').strip()
                for topic in topics_part.replace(' and ', ',').split(',')
            ]
            
            # Create query for multiple topics
            from django.db.models import Q
            query = Q()
            for topic in topics:
                query |= (
                    Q(title__icontains=topic) |
                    Q(topic__icontains=topic) |
                    Q(content__icontains=topic)
                )

            # Get notes matching any of the topics
            related_notes = Note.objects.filter(
                module=quiz.module
            ).filter(query).distinct()
            
            logger.debug(f"Quiz topics: {topics}")
            logger.debug(f"Found {related_notes.count()} related notes")

            if result.percentage >= 80:
                return Response({
                    "performance_message": "Excellent work! Keep it up!"
                })

            suggestions = {
                "study_suggestions": [
                    f"Review the material for Quiz on: {', '.join(topics).upper()} Notes",
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
                    } for note in related_notes
                ]
            }

            return Response(suggestions)

        except QuizResult.DoesNotExist:
            return Response(
                {"error": "Quiz result not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in QuizSuggestionsView: {e}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )