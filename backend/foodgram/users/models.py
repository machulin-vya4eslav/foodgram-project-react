from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USERNAME_FIELD = 'email'

    email = models.EmailField(
        verbose_name='email',
        max_length=254,
        unique=True
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )

    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь,'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Подписчик'
    )

    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]
