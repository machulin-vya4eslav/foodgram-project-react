from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT
)
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingList,
    Tag
)

from .serializers import (
    RecipeWriteSerializer,
    TagSerializer,
    RecipeReadSerializer,
    ShortRecipeSerializer,
    IngredientSerializer
)
from .permissions import IsAdminOrReadOnly, IsAdminOrIsAuthorOrReadOnly
from .pagination import CustomListPagination
from .filters import IngredientListFilter, RecipeListFilter


class TagViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с объектами модели Tag.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с объектами модели Ingredient.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientListFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для работы с объектами модели Recipe.
    """

    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer
    pagination_class = CustomListPagination
    permission_classes = (IsAdminOrIsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeListFilter

    def get_serializer_class(self):
        """
        Метод, выбирающий сериализатор в записимости от типа запроса.

        Для безопасных запросов - RecipeReadSerializer
        Для не безопасных - RecipeWriteSerializer.
        """

        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        """
        Метод, добавляющий в сериализитор автора поста.
        """

        serializer.save(author=self.request.user)

    def _favorite_or_shopping_cart(self, request, pk, model, text_in_err):
        """
        Метод, добавляющий эндпоинт favorite.
        """

        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':

            _, is_created = model.objects.get_or_create(
                user=user,
                recipe=recipe
            )

            if not is_created:
                return Response(
                    {'error': f'Рецепт уже есть в {text_in_err}'},
                    status=HTTP_400_BAD_REQUEST
                )

            serializer = ShortRecipeSerializer(recipe)

            return Response(serializer.data, status=HTTP_201_CREATED)

        obj = model.objects.filter(user=user, recipe__id=pk)

        if not obj.exists():
            return Response(
                {'error': f'Рецепт не в {text_in_err}, нечего удалять'},
                status=HTTP_400_BAD_REQUEST
            )
        obj.delete()

        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        """
        Метод, добавляющий эндпоинт favorite.
        """

        text_in_err = r'"Избранное"'

        return self._favorite_or_shopping_cart(
            request,
            pk,
            Favorite,
            text_in_err
        )

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        """
        Метод, добавляющий эндпоинт shopping_cart.
        """

        text_in_err = r'"Список покупок"'

        return self._favorite_or_shopping_cart(
            request,
            pk,
            ShoppingList,
            text_in_err
        )

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        user = request.user

        if not user.shopping_list.exists():
            return Response(
                {'errors': 'В списке покупок пусто, нечего скачивать'},
                status=HTTP_400_BAD_REQUEST
            )

        ingredients = IngredientInRecipe.objects.filter(
            recipe__shopping_list__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            amount=Sum('amount')
        ).order_by(
            'ingredient__name'
        )

        shopping_cart = ''

        for number, ingredient in enumerate(ingredients, start=1):
            shopping_cart += (
                f'{number}) {ingredient["ingredient__name"].capitalize()}'
                f' — {ingredient["amount"]}'
                f'{ingredient["ingredient__measurement_unit"]}.\n'
            )

        filename = f'{user.username}_shopping_cart.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'

        return response
