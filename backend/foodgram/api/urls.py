from rest_framework import routers
from django.urls import include, path

from .views import TagViewsSet


v1_router = routers.DefaultRouter()

# v1_router.register(r'recipes')
v1_router.register(r'tags', TagViewsSet)

urlpatterns = [
    path('v1/', include(v1_router.urls))
]
