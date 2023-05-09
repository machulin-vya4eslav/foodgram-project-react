from djoser.views import UserViewSet
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT
)

from .models import User, Follow
from api.serializers import CustomUserSerializer, SubscribeSirializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, pk):
        user = request.user
        author = User.objects.get(id=pk)

        if user == author:
            return Response(
                {'error': 'Вы не можете от(под)писываться сами на себя'},
                status=HTTP_400_BAD_REQUEST)

        if request.method == 'POST':

            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'error': 'Вы уже подписаны на этого автора'},
                    status=HTTP_400_BAD_REQUEST)

            Follow.objects.create(user=user, author=author)
            serializer = SubscribeSirializer(
                author, context={"request": request}
            )

            return Response(
                serializer.data,
                status=HTTP_201_CREATED
            )

        if request.method == 'DELETE':

            obj = Follow.objects.filter(user=user, author=author)

            if not obj.exists():
                return Response(
                    {'error': 'Вы не подписаны на этого автора'},
                    status=HTTP_400_BAD_REQUEST)

            obj.delete()

            return Response(status=HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        pass