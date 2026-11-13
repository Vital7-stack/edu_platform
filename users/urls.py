from django.urls import path
from users.views import UserListAPIView, UserRetrieveUpdateAPIView, PaymentListAPIView

urlpatterns = [
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserRetrieveUpdateAPIView.as_view(), name='user-list-detail'),
    path('payments/', PaymentListAPIView.as_view(), name='payment-list'),
]