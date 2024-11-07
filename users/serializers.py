from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
from courses.serializers import CourseSerializer  # Assuming you have this serializer
from courses.models import Course 
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'image']
        
        
    def get_enrolled_courses(self, obj):
        if obj.role == 'student':
            # Only include enrolled courses if the user is a student
            courses = Course.objects.filter(students=obj)
            return CourseSerializer(courses, many=True).data
        return []

    def get_created_courses(self, obj):
        if obj.role == 'teacher':
            # Only include created courses if the user is a teacher
            courses = Course.objects.filter(created_by=obj)
            return CourseSerializer(courses, many=True).data
        return []

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'role', 'image']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        image = validated_data.pop('image', None)
        user = User.objects.create_user(**validated_data)
        
        if image:
            user.image = image
            user.save()

        return user

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['name'] = user.get_full_name()
        token['email'] = user.email
        token['role'] = user.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add custom response data
        data.update({
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'first_name': self.user.first_name,
                'last_name': self.user.last_name,
                'role': self.user.role,
                'image': self.user.image.url if self.user.image else None,
            }
        })

        return data

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User is deactivated.')
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        data['user'] = user
        return data
