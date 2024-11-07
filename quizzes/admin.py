from django.contrib import admin
from .models import Quiz, Question, Result, StudentAnswer

# Inline model for Questions within a Quiz
class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1  # Number of extra blank fields for adding new questions
    fields = ('question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer')

# Admin configuration for the Quiz model
@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'created_by', 'quiz_type', 'category', 'created_at', 'quiz_duration')
    search_fields = ('title', 'module__name', 'created_by__username')
    list_filter = ('quiz_type', 'category', 'created_at')
    inlines = [QuestionInline]  # Inline questions for the quiz

    def get_queryset(self, request):
        """Customize the queryset for the admin interface."""
        queryset = super().get_queryset(request)
        return queryset.select_related('module', 'created_by')

# Admin configuration for the Question model
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'correct_answer')
    search_fields = ('question_text', 'quiz__title')
    list_filter = ('quiz__category',)

# Admin configuration for the Result model
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'score', 'date_taken')
    search_fields = ('quiz__title', 'student__username')
    list_filter = ('quiz__title', 'date_taken')

# Admin configuration for the StudentAnswer model
@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'student', 'selected_option', 'answer_text')
    search_fields = ('question__question_text', 'student__username')
    list_filter = ('question__quiz__title',)
