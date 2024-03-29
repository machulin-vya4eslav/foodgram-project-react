from django_filters.rest_framework import filters, FilterSet

from recipes.models import Ingredient, Recipe, Tag


class IngredientListFilter(FilterSet):
    """
    Фильтр для ингредиентов.

    Ищет по начальному вхождению в поле name.
    """

    name = filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeListFilter(FilterSet):
    """
    Фильтр для рецептов.

    Ищет по slug модели Tag, а также по вхождению или
    невхождению в список покупок и список избранного
    """

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
        )

    def is_favorited_filter(self, queryset, name, value):
        """
        Метод формирующий фильтр по вхождению в избранное.
        """

        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        """
        Метод формирующий фильтр по вхождению в список покупок.
        """

        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_list__user=user)
        return queryset
