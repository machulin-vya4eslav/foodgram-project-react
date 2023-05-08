from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    USERNAME_FIELD = 'email'

    email = models.EmailField(
        verbose_name='email',
        max_length=254,
        unique=True
    )

    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользовател,'
        verbose_name_plural = 'Пользователи'
