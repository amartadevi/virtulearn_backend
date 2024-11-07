from django.contrib import admin
from .models import EnrollmentRequest

# Customizing the admin panel for EnrollmentRequest
class EnrollmentRequestAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = ('student_username', 'course_name', 'status')

    # Add filters to the right sidebar for filtering by status and course
    list_filter = ('status', 'course')

    # Add search functionality for student and course name
    search_fields = ('student__username', 'course__name')

    # Read-only fields for course name and student username
    readonly_fields = ('course_name', 'student_username')

    # Override the get_queryset method to show more descriptive info in admin
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('course', 'student')
        return queryset

    # Method to retrieve the course name for display
    def course_name(self, obj):
        return obj.course.name
    course_name.short_description = 'Course Name'

    # Method to retrieve the student username for display
    def student_username(self, obj):
        return obj.student.username
    student_username.short_description = 'Student Username'

    # Enable editing of enrollment request status directly from the list view
    list_editable = ('status',)

    # Add CRUD actions (create, update, delete) to manage enrollment requests
    actions = ['approve_requests', 'deny_requests']

    # Action to approve selected enrollment requests
    def approve_requests(self, request, queryset):
        updated = queryset.update(status='approved')
        for enrollment in queryset:
            enrollment.course.students.add(enrollment.student)
        self.message_user(request, f"{updated} enrollment request(s) approved.")
    approve_requests.short_description = "Approve selected requests"

    # Action to deny selected enrollment requests
    def deny_requests(self, request, queryset):
        updated = queryset.update(status='denied')
        self.message_user(request, f"{updated} enrollment request(s) denied.")
    deny_requests.short_description = "Deny selected requests"

# Register the admin class with the EnrollmentRequest model
admin.site.register(EnrollmentRequest, EnrollmentRequestAdmin)
