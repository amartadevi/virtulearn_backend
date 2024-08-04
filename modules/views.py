from rest_framework import generics
from .models import Module
from .serializers import ModuleSerializer
from rest_framework.permissions import IsAuthenticated

class ModuleListCreateView(generics.ListCreateAPIView):
    # queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.request.query_params.get('course_id')
        if course_id:
            return Module.objects.filter(course_id=course_id)
        return Module.objects.none()  # or handle the case as needed

class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
