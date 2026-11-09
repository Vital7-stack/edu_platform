from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Менеджер, который учит Django создавать юзеров по email."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('У пользователя должен быть указан email')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # хешируем пароль, а не храним как есть
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name='Email')
    first_name = models.CharField(max_length=100, verbose_name='Имя', blank=True)
    last_name = models.CharField(max_length=100, verbose_name='Фамилия', blank=True)
    phone = models.CharField(max_length=35, verbose_name='Телефон', blank=True)
    city = models.CharField(max_length=100, verbose_name='Город', blank=True)
    avatar = models.ImageField(upload_to='users/avatars/', verbose_name='Аватарка', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'   # <- авторизация по email вместо username
    REQUIRED_FIELDS = []       # при createsuperuser дополнительное не спрашиваем

    objects = UserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
