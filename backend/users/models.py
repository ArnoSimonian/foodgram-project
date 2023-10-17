from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .constants import MAX_EMAIL_LENGTH, MAX_USER_VALUE_LENGTH
from .validators import (validate_first_name, validate_last_name,
                         validate_username)


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    username = models.CharField(
        verbose_name='имя пользователя',
        max_length=MAX_USER_VALUE_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator(),
                    validate_username],
    )
    email = models.EmailField(
        verbose_name='email',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
    )
    first_name = models.CharField(
        verbose_name='имя',
        max_length=MAX_USER_VALUE_LENGTH,
        validators=[validate_first_name],
    )
    last_name = models.CharField(
        verbose_name='фамилия',
        max_length=MAX_USER_VALUE_LENGTH,
        validators=[validate_last_name],
    )

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
