from django.urls import path
from users.views import UserListAPIView, UserRetrieveUpdateAPIView

urlpatterns = [
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserRetrieveUpdateAPIView.as_view(), name='user-detail'),
]