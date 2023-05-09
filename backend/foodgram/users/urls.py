from rest_framework import routers
from django.urls import include, path

from .views import CustomUserViewSet


router = routers.DefaultRouter()

router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
