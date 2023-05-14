from django.contrib import admin
from django.contrib.admin import display

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingList,
    Tag
)


class IngredientAdmin(admin.ModelAdmin):
    """
    Настройки обображения в админке объектов Ingredient.
    """

    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


class TagAdmin(admin.ModelAdmin):
    """
    Настройки обображения в админке объектов Tag.
    """

    list_display = ('name', 'color', 'slug',)


class RecipeAdmin(admin.ModelAdmin):
    """
    Настройки обображения в админке объектов Recipe.
    """

    list_display = ('name', 'author', 'added_in_favorites',)
    readonly_fields = ('added_in_favorites',)
    list_filter = ('author', 'name', 'tags',)

    @display(description='Количество в избранных')
    def added_in_favorites(self, obj):
        """
        Добавляет в админку общее количество добавлений в избранное.
        """

        return obj.favorites.count()


class ShoppingListAdmin(admin.ModelAdmin):
    """
    Настройки обображения в админке объектов ShoppingList.
    """

    list_display = ('user', 'recipe',)


class FavouriteAdmin(admin.ModelAdmin):
    """
    Настройки обображения в админке объектов Favourite.
    """

    list_display = ('user', 'recipe',)


class IngredientInRecipeAdmin(admin.ModelAdmin):
    """
    Настройки обображения в админке объектов Ingredient.
    """

    list_display = ('recipe', 'ingredient', 'amount',)


admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(Favorite, FavouriteAdmin)
admin.site.register(IngredientInRecipe, IngredientInRecipeAdmin)
