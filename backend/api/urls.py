from rest_framework import routers
from django.urls import include, path

from .views import TagViewSet, RecipeViewSet, IngredientViewSet


router = routers.DefaultRouter()

router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls))
]
