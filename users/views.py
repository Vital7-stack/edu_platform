from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, CreateAPIView, DestroyAPIView
from rest_framework import permissions

from users.models import User, Payment
from users.permissions import IsModerator, IsProfileOwner
from users.serializers import UserSerializer, PaymentSerializer, UserCreateSerializer


class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    """Профиль пользователя: смотреть и редактировать может сам пользователь или модератор."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsModerator | IsProfileOwner]


class UserDestroyAPIView(DestroyAPIView):
    """Удаление пользователя — только модератору."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsModerator]


class PaymentListAPIView(ListAPIView):
    """GET /api/payments/ — список платежей с фильтрацией и сортировкой."""
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']
    ordering_fields = ['payment_date']

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Payment.objects.all()
        return Payment.objects.filter(user=user)
