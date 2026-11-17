from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import (
    UserListAPIView,
    UserRetrieveUpdateAPIView,
    UserDestroyAPIView,
    PaymentListAPIView,
    UserCreateAPIView,
)

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='user-register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserRetrieveUpdateAPIView.as_view(), name='user-list-detail'),
    path('users/<int:pk>/delete/', UserDestroyAPIView.as_view(), name='user-delete'),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
]