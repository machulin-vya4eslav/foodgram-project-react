from rest_framework import decorators, viewsets
from rest_framework.permissions import SAFE_METHODS

from recipes.models import Recipe, Tag
from .serializers import RecipeWriteSerializer, TagSerializer, RecipeReadSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    # permission_classes = (permissions.A) Только чтение или если админ


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeWriteSerializer

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @decorators.action(
            methods=['get'],
            detail=False
    )
    def download_shopping_cart(self, request):
        pass
