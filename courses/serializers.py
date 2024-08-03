from rest_framework import serializers
from .models import Course
from users.models import User

class CourseSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    students = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all(), many=True, required=False)
    is_student = serializers.SerializerMethodField()
    is_teacher = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'created_by', 'students', 'is_student', 'is_teacher']
        read_only_fields = ['code']

    def get_created_by(self, obj):
        return {
            'username': obj.created_by.username,
            'role': obj.created_by.role
        }

    def get_is_student(self, obj):
        request = self.context.get('request')
        return request.user in obj.students.all()

    def get_is_teacher(self, obj):
        request = self.context.get('request')
        return obj.created_by == request.user

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'students' in validated_data:
            students = validated_data.pop('students')
            instance.students.set(students)
        return super().update(instance, validated_data)