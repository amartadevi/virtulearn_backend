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
        quiz = self.get_quiz()
        return Result.objects.filter(quiz=quiz)

    def get_quiz(self):
        try:
            return Quiz.objects.get(pk=self.kwargs['quiz_pk'], module_id=self.kwargs['module_pk'])
        except Quiz.DoesNotExist:
            raise NotFound("Quiz not found.")

    def perform_create(self, serializer):
        quiz = self.get_quiz()
        score = self.calculate_score(quiz, self.request.user)
        serializer.save(quiz=quiz, student=self.request.user, score=score)

    def calculate_score(self, quiz, student):
        correct_answers = 0
        total_questions = quiz.questions.count()
        if total_questions == 0:
            return 0
        student_answers = StudentAnswer.objects.filter(question__quiz=quiz, student=student)
        for answer in student_answers:
            if answer.selected_option == answer.question.correct_answer:
                correct_answers += 1
        return (correct_answers / total_questions) * 100

class ResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Result.objects.filter(quiz__module_id=self.kwargs['module_pk'])
    
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



