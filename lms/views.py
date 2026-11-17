from rest_framework import viewsets, permissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from lms.models import Course, Lesson
from lms.permissions import IsModerator, IsOwner
from lms.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """Полный CRUD для курса одним классом."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

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

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()


class LessonRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /lessons/<pk>/ — один урок."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        if self.action in ('update', 'partial_update'):
            self.permission_classes = [permissions.IsAuthenticated, IsModerator | IsOwner]
        elif self.action == 'destroy':
            self.permission_classes = [permissions.IsAuthenticated, ~IsModerator]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return super().get_permissions()
