from rest_framework import routers
from rest_framework.authtoken import views
from django.urls import include, path

from .views import TagViewSet, RecipeViewSet


v1_router = routers.DefaultRouter()

v1_router.register('recipes', RecipeViewSet)
v1_router.register('tags', TagViewSet)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('api-token-auth/', views.obtain_auth_token)
]
