from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator


User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=50
    )

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
    color_hex_code = models.CharField(
        'Цветовой HEX-код',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не является цветом в формате HEX!'
            )
        ]
    )
    slug = models.SlugField(verbose_name='Слаг', unique=True, max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(verbose_name='Фото', upload_to='recipes/')
    cooking_time = models.PositiveSmallIntegerField('Время приготовления')
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        related_name='recipes',
        verbose_name='Теги'
    )

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='',
        on_delete=models.CASCADE
    )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег',
        on_delete=models.CASCADE
    )    
