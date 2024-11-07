from rest_framework import generics
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer, MyTokenObtainPairSerializer, LoginSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from courses.serializers import CourseSerializer  # Assuming you have this serializer
from courses.models import Course 
from rest_framework import status

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Allow any user to access this view

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Fetch enrolled and created courses
        enrolled_courses = Course.objects.filter(students=user)
        created_courses = Course.objects.filter(created_by=user)
        
        # Pass the request context to the serializer to access the user
        enrolled_courses_data = CourseSerializer(enrolled_courses, many=True, context={'request': request}).data
        created_courses_data = CourseSerializer(created_courses, many=True, context={'request': request}).data

        # Prepare the profile data
        profile_data = {
            'user': UserSerializer(user).data,
            'enrolled_courses': enrolled_courses_data,
            'created_courses': created_courses_data
        }

        return Response(profile_data, status=status.HTTP_200_OK)

class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class LoginView(MyTokenObtainPairView):
    # You can now use this view for login
    pass
