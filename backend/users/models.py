from django.contrib.auth.models import AbstractUser
from django.db import models


MAX_LENGTH_EMAIL = 254
MAX_LENGTH_FIRST_AND_LAST_NAME = 150


class User(AbstractUser):
    """
    Переопределенный класс пользователя.

    Позволяет авторизовываться по email.
    """

    USERNAME_FIELD = 'email'

    email = models.EmailField(
        verbose_name='email',
        max_length=MAX_LENGTH_EMAIL,
        unique=True
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=MAX_LENGTH_FIRST_AND_LAST_NAME
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=MAX_LENGTH_FIRST_AND_LAST_NAME
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
    """
    Модель для хранения информации о подписчиках.

    Связывает пользователя и авторов, на которых он подписан.
    """
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
