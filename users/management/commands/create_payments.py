import random
from decimal import Decimal

from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

from lms.models import Course, Lesson
from users.models import User, Payment


class Command(BaseCommand):
    help = 'Заполняет таблицу платежей тестовыми данными'

    def handle(self, *args, **options):
        users = list(User.objects.all())
        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        if not users:
            self.stdout.write(self.style.ERROR('Сначала создайте пользователей (суперпользователя)'))
            return

        # Очистим старые тестовые платежи, чтобы команда была перезапускаемой
        Payment.objects.all().delete()

        now = timezone.now()
        count = 0

        for i, user in enumerate(users):
            method = random.choice([Payment.CASH, Payment.TRANSFER])

            # Платёж за курс, если курсы есть
            if courses:
                Payment.objects.create(
                    user=user,
                    paid_course=courses[i % len(courses)],
                    amount=Decimal('9900.00'),
                    payment_method=method,
                )
                count += 1

            # Платёж за урок, если уроки есть
            if lessons:
                Payment.objects.create(
                    user=user,
                    paid_lesson=lessons[i % len(lessons)],
                    amount=Decimal('990.00'),
                    payment_method=method,
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(f'Создано платежей: {count}'))