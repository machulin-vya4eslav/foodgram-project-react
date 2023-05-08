from rest_framework import routers
from django.urls import include, path

from .views import TagViewSet, RecipeViewSet


router = routers.DefaultRouter()

router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('', include('djoser.urls.authtoken'))
]
