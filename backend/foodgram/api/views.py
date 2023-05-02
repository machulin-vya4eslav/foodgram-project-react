from rest_framework import viewsets

from recipes.models import Tag
from .serializers import TagSerializer


class TagViewsSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
