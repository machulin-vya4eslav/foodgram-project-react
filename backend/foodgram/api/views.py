from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT
)
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS

from recipes.models import Recipe, Tag, Favorite, ShoppingList, Ingredient
from .serializers import (
    RecipeWriteSerializer,
    TagSerializer,
    RecipeReadSerializer,
    ShortRecipeSerializer,
    IngredientSerializer
)
from .permissions import IsAdminOrReadOnly


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly, )


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        user = request.user
        if request.method == 'POST':

            if Favorite.objects.filter(user=user, recipe__id=pk).exists():
                return Response(
                    {'error': 'Рецепт уже есть в избранном'},
                    status=HTTP_400_BAD_REQUEST
                )

            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.create(recipe=recipe, user=user)
            serializer = ShortRecipeSerializer(recipe)

            return Response(serializer.data, status=HTTP_201_CREATED)

        obj = Favorite.objects.filter(user=user, recipe__id=pk)

        if not obj.exists():
            return Response(
                {'error': 'Рецепт не добавлен в избранное, нечего удалять'},
                status=HTTP_400_BAD_REQUEST
            )

        obj.delete()
        return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        user = request.user
        if request.method == 'POST':

            if ShoppingList.objects.filter(user=user, recipe__id=pk).exists():
                return Response(
                    {'error': 'Рецепт уже есть в списке покупок'},
                    status=HTTP_400_BAD_REQUEST
                )

            recipe = get_object_or_404(Recipe, id=pk)
            ShoppingList.objects.create(recipe=recipe, user=user)
            serializer = ShortRecipeSerializer(recipe)

            return Response(serializer.data, status=HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = ShoppingList.objects.filter(user=user, recipe__id=pk)

            if not obj.exists():
                return Response(
                    {'error': 'Рецепт не добавлен в покупки, нечего удалять'},
                    status=HTTP_400_BAD_REQUEST
                )

            obj.delete()
            return Response(status=HTTP_204_NO_CONTENT)
