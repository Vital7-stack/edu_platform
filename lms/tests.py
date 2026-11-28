from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import IntegrityError
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson, Subscription

User = get_user_model()


class LessonCRUDTests(APITestCase):

    def setUp(self):
        self.owner = User.objects.create_user(email='owner@t.ru', password='12345')
        self.moderator = User.objects.create_user(email='mod@t.ru', password='12345')
        self.moderator.groups.add(Group.objects.get_or_create(name='moderators')[0])
        self.other_user = User.objects.create_user(email='other@t.ru', password='12345')

        self.course = Course.objects.create(name='Тестовый курс', owner=self.owner)
        self.lesson = Lesson.objects.create(name='Тестовый урок', course=self.course, owner=self.owner)

    def test_create_lesson(self):
        """Создание урока: владелец проставляется автоматически."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/lessons/', {
            'name': 'Новый урок',
            'course': self.course.pk,
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.filter(name='Новый урок').count(), 1)

    def test_delete_lesson(self):
        """Удаление своего урока."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(f'/api/lessons/{self.lesson.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_retrieve_lesson(self):
        """Получение отдельного урока."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/lessons/{self.lesson.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Тестовый урок')

    def test_lesson_youtube_url_allowed(self):
        """Ссылка на YouTube проходит валидацию."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/lessons/', {
            'name': 'Урок с видео',
            'course': self.course.pk,
            'video_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_invalid_url_blocked(self):
        """Ссылка на сторонний ресурс блокируется валидатором."""
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/lessons/', {
            'name': 'Урок с чужим видео',
            'course': self.course.pk,
            'video_url': 'https://vimeo.com/123456',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_moderator_can_update_lesson(self):
        """Модератор может редактировать чужой урок."""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.patch(f'/api/lessons/{self.lesson.pk}/', {'name': 'Обновлено'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_cannot_update_foreign_lesson(self):
        """Обычный пользователь не может редактировать чужой урок (для него он 404)."""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.patch(f'/api/lessons/{self.lesson.pk}/', {'name': 'Взлом'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_moderator_cannot_delete_lesson(self):
        """Модератору запрещено удалять уроки (по логике проекта)."""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f'/api/lessons/{self.lesson.pk}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SubscriptionTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(email='user@t.ru', password='12345')
        self.course = Course.objects.create(name='Курс', owner=self.user)
        self.client.force_authenticate(user=self.user)
        self.url = f'/api/courses/{self.course.pk}/subscription/'

    def test_subscribe(self):
        """Первая подписка добавляется."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'подписка добавлена')
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_is_subscribed_in_course_detail(self):
        """После подписки в сериализаторе курса is_subscribed=True."""
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.get(f'/api/courses/{self.course.pk}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_subscribed'])

    def test_unsubscribe(self):
        """Повторный POST удаляет подписку — логика toggle."""
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_duplicate_not_created(self):
        """Уникальная пара пользователь-курс: дубль не создаётся."""
        Subscription.objects.create(user=self.user, course=self.course)
        with self.assertRaises(IntegrityError):
            Subscription.objects.create(user=self.user, course=self.course)