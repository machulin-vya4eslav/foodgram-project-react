from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator


User = get_user_model()


MIN_COOCING_TIME = 1
MIN_AMOUNT_INGREDIENTS = 1

MAX_LENGTH_NAME = 200
MAX_LENGTH_TAG_SLUG = 50
MAX_LENGTH_MEASUREMENT_UNIT = 50
MAX_LENGTH_HEX_COLOR = 8


class Ingredient(models.Model):
    """
    Модель ингредиентов.
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=MAX_LENGTH_MEASUREMENT_UNIT
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
    Модель тегов.
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME
    )
    color = models.CharField(
        verbose_name='Цвет в HEX',
        unique=True,
        max_length=MAX_LENGTH_HEX_COLOR,
        validators=[
            RegexValidator(
                regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$',
                message='Введенное значение не в HEX формате'
            )
        ]
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
        max_length=MAX_LENGTH_TAG_SLUG
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель рецептов.
    """

    name = models.CharField(
        verbose_name='Название',
        max_length=MAX_LENGTH_NAME
    )
    text = models.TextField(verbose_name='Описание')
    image = models.ImageField(
        verbose_name='Фото рецепта',
        upload_to='recipes/',
    )
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

    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created']

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """
    Модель для связи ингредиентов и рецептов.
    """

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

    def __str__(self) -> str:
        return (f'Ингредиент {self.ingredient.name} '
                f'в рецепте {self.recipe.name} - '
                f'{self.amount}{self.ingredient.measurement_unit}')

    class Meta:
        verbose_name = 'Ингридиент в рецепте'
        verbose_name_plural = 'Ингридиенты в рецепте'


class RecipeTag(models.Model):
    """
    Модель для связи тегов и рецептов.
    """

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


class Favorite(models.Model):
    """
    Модель для избранного.

    Связывает пользователя и рецепт, позволяет хранить информацию
    о добавлении в избранное рецепта.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        )

    def __str__(self):
        return f'{self.user} добавил рецепт {self.recipe} в избранное'


class ShoppingList(models.Model):
    """
    Модель для списка покупок.

    Связывает пользователя и рецепт, позволяет хранить информацию
    о добавлении в список покупок рецепта.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list'
            )
        ]

    def __str__(self):
        return f'{self.user} добавил рецепт {self.recipe} в список покупок'
