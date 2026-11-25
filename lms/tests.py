from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Lesson, Course


class LessonCRUDTestCase(APITestCase):
    def setUp(self):
        # Обычный пользователь
        self.user = get_user_model().objects.create_user(
            email="user@test.com", password="test1234", city="Тест"
        )
        # Модератор
        self.moderator = get_user_model().objects.create_user(
            email="mod@test.com", password="test1234", city="Тест"
        )
        # Чужой пользователь (не владелец)
        self.stranger = get_user_model().objects.create_user(
            email="stranger@test.com", password="test1234", city="Тест"
        )
        self.course = Course.objects.create(name="Тестовый курс", owner=self.user)
        self.lesson = Lesson.objects.create(
            name="Тестовый урок", course=self.course,
            video_url="https://youtube.com/watch?v=1", owner=self.user,
        )

    def _auth(self, user):
        self.client.force_authenticate(user=user)

    def test_create_lesson_with_valid_url(self):
        self._auth(self.user)
        response = self.client.post(
            "/api/lessons/",
            {"name": "Урок", "video_url": "https://youtube.com/watch?v=x", "course": self.course.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_with_invalid_url(self):
        self._auth(self.user)
        response = self.client.post(
            "/api/lessons/",
            {"name": "Урок", "video_url": "https://stepik.org/1", "course": self.course.id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_owner_can_update_lesson(self):
        self._auth(self.user)
        response = self.client.patch(f"/api/lessons/{self.lesson.id}/", {"name": "Обновлён"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_stranger_cannot_delete_lesson(self):
        self._auth(self.stranger)
        response = self.client.delete(f"/api/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_owner_can_delete_lesson(self):
        self._auth(self.user)
        response = self.client.delete(f"/api/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_gets_401(self):
        response = self.client.get("/api/lessons/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)