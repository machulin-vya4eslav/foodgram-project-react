from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator


User = get_user_model()


MIN_COOCING_TIME = 1
MIN_AMOUNT_INGREDIENTS = 1


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
    color = models.CharField(
        verbose_name='Цвет в HEX',
        unique=True,
        max_length=7,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не в HEX формате'
            )
        ]
    )
    slug = models.SlugField(verbose_name='Слаг', unique=True, max_length=50)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200)
    text = models.TextField(verbose_name='Описание')
    # image = models.ImageField(
    #     verbose_name='Фото рецепта',
    #     upload_to='recipes/'
    # )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        validators=[
            MinValueValidator(
                MIN_COOCING_TIME,
                message=f'Минимальное значение {MIN_COOCING_TIME}'
            )
        ]
    )
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор публикации'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
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


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='ingredientinrecipe',
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        related_name='ingredientinrecipe',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_AMOUNT_INGREDIENTS,
                message=f'Минимальное значение {MIN_AMOUNT_INGREDIENTS}'
            )
        ]
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
