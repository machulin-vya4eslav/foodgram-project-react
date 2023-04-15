from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Ingredient(models.Model):
    pass


class Tag(models.Model):
    pass


class Recipe(models.Model):
    name = models.TextField(verbose_name='Название', max_length=200)
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(verbose_name='Фото', upload_to='recipes/')
    cooking_time = models.PositiveSmallIntegerField('Время приготовления', )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    # ingredients = models.ManyToManyField(
    #     Ingredient,
    #     through='RecipeIngredient',
    #     related_name='recipes',
    #     verbose_name='Ингредиенты'
    # )
    # tags = models.ManyToManyField(
    #     Tag,
    #     through='RecipeTag',
    #     related_name='recipes',
    #     verbose_name='Теги'
    # )


class RecipeIngredient(models.Model):
    pass


class RecipeTag(models.Model):
    pass
