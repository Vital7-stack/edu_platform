from rest_framework import serializers

from validators import validate_video_url
from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.email')
    video_url = serializers.URLField(validators=[validate_video_url])

    class Meta:
        model = Lesson
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'description', 'preview', 'lessons_count', 'lessons', 'owner']

    def get_lessons_count(self, course):
        return course.lessons.count()