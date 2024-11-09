from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from .models import QuizResult, Quiz 
from .serializers import ResultSerializer
from rest_framework import status



class ResultListCreateView(generics.ListCreateAPIView):
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Result.objects.filter(
            quiz_id=self.kwargs['quiz_pk'],
            quiz__module_id=self.kwargs['module_pk']
        )

    def perform_create(self, serializer):
        quiz_content = self.request.data.get('quiz_content')
        percentage = self.request.data.get('percentage')
        
        # Create the result
        serializer.save(
            quiz_id=self.kwargs['quiz_pk'],
            student=self.request.user,
            score=percentage,
            answers=quiz_content  # Store the detailed answers
        )

class ResultDetailView(generics.RetrieveAPIView):
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Result.objects.filter(
            quiz_id=self.kwargs['quiz_pk'],
            quiz__module_id=self.kwargs['module_pk']
        )

# quizzes/views.py

from rest_framework.response import Response
from rest_framework import generics, status
from .serializers import QuizResultSerializer
from .models import Quiz  # Ensure Quiz model is imported

class SubmitQuizResult(generics.CreateAPIView):
    serializer_class = QuizResultSerializer

    def post(self, request, quiz_pk):
        # Log incoming data for debug purposes
        print(f"Received quiz submission data: {request.data}")

        if 'answers' not in request.data:
            return Response({'error': 'Answers are required.'}, status=status.HTTP_400_BAD_REQUEST)

        student_id = request.user.id  # Get the current logged-in user's ID
        answers = request.data['answers']
        score = self.calculate_score(answers)  # Calculate score based on answers

        serializer = self.get_serializer(data={
            'student': student_id,
            'quiz': quiz_pk,
            'score': score,
            'answers': answers,
        })
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Quiz result saved successfully'}, status=status.HTTP_201_CREATED)

        print(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



