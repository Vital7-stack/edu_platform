from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from paginators import LessonPaginator, CoursePaginator

from lms.models import Course, Lesson, Subscription
from lms.permissions import IsModerator, IsOwner
from lms.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """Полный CRUD для курса одним классом."""

    serializer_class = CourseSerializer
    pagination_class = CoursePaginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.action in ('list', 'retrieve', 'update', 'partial_update'):
            self.permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        return super().get_permissions()


class LessonListCreateAPIView(ListCreateAPIView):
    """GET /lessons/ — список уроков, POST /lessons/ — создать урок."""

    serializer_class = LessonSerializer
    pagination_class = LessonPaginator

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:  # GET — список
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class LessonRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /lessons/<pk>/ — один урок."""

    serializer_class = LessonSerializer

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        elif self.request.method in ('PUT', 'PATCH'):
            self.permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        else:  # GET — просмотр одного урока
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class SubscriptionToggleAPIView(APIView):
    """POST: добавляет подписку, если её нет, и удаляет, если она есть."""

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        subscription, created = Subscription.objects.get_or_create(
            user=request.user, course=course
        )
        if created:
            message = 'подписка добавлена'
        else:
            subscription.delete()
            message = 'подписка удалена'
        return Response({'message': message}, status=status.HTTP_200_OK)