from django.urls import path
from .views import DiscussionListCreateView, DiscussionDetailView

urlpatterns = [
    path('', DiscussionListCreateView.as_view(), name='discussion-list-create'),
    path('<int:pk>/', DiscussionDetailView.as_view(), name='discussion-detail'),
]
