from rest_framework import serializers

from validators import validate_video_url
from lms.models import Course, Lesson, Subscription


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
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'description', 'preview',
            'lessons_count', 'lessons', 'owner', 'is_subscribed',
        ]

    def get_lessons_count(self, course):
        return course.lessons.count()

    def get_is_subscribed(self, course):
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False
        return Subscription.objects.filter(user=request.user, course=course).exists()