from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .utils import (EMAIL_LENGTH, FIRST_NAME_LENGTH, LAST_NAME_LENGTH,
                    PASSWORD_LENGTH, USERNAME_LENGTH)
from .validators import validate_username


class User(AbstractUser):
    USER = 'user'
    ADMIN = 'admin'

    ROLE_CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.CharField(
        verbose_name='имя пользователя',
        max_length=USERNAME_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator(),
                    validate_username],
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=EMAIL_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='имя',
        max_length=FIRST_NAME_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=LAST_NAME_LENGTH,
    )
    password = models.CharField(
        verbose_name='пароль',
        max_length=PASSWORD_LENGTH,
    )
    role = models.CharField(
        verbose_name='уровень доступа',
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        choices=ROLE_CHOICES,
        default=USER,
        blank=True,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser or self.is_staff

    class Meta:
        ordering = ('-username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.username


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    subscribing = models.ForeignKey(
        User,
        verbose_name='подписки пользователя',
        on_delete=models.CASCADE,
        related_name='subscribing',
    )

    class Meta:
        ordering = ('-user',)
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(subscribing=models.F('user')),
                name='could_not_subscribe_itself',
            ),
            models.UniqueConstraint(
                fields=['user', 'subscribing'],
                name='unique_subscribing',
            ),
        ]

    def __str__(self):
        return f'{self.user.username}: {self.subscribing.username}'
