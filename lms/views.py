from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from lms.models import Course, Lesson
from lms.serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """Полный CRUD для курса одним классом."""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class LessonListCreateAPIView(ListCreateAPIView):
    """GET /lessons/ — список уроков, POST /lessons/ — создать урок."""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE /lessons/<pk>/ — один урок."""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
