from django.db.models import Count
from rest_framework import serializers

from lms.serializers import CourseSerializer, LessonSerializer
from users.models import User, Payment


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone', 'city', 'avatar')

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class PaymentSerializer(serializers.ModelSerializer):
    paid_course = CourseSerializer(read_only=True)
    paid_lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone', 'city', 'avatar', 'payments')
        read_only_fields = ('email',)