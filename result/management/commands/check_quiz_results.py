from django.core.management.base import BaseCommand
from result.models import QuizResult

class Command(BaseCommand):
    help = 'Check quiz results in the database'

    def handle(self, *args, **options):
        self.stdout.write('Checking quiz results...')
        
        results = QuizResult.objects.all()
        for result in results:
            self.stdout.write(f'\nQuiz: {result.quiz_id}')
            self.stdout.write(f'Student: {result.student_id}')
            self.stdout.write(f'Score: {result.score}')
            self.stdout.write(f'Answers: {result.student_answers}') 