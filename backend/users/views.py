from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_200_OK
)

from djoser.views import UserViewSet

from .models import User, Follow
from api.serializers import CustomUserSerializer, SubscribeSirializer
from api.pagination import CustomListPagination


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет для объектов модели User.
    """

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomListPagination

    @action(
            methods=['post', 'delete'],
            detail=True,
            permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        """
        Добавляет эндпоинт для подписки subscribe.
        """

        user = request.user
        author = User.objects.get(id=id)

        if user == author:
            return Response(
                {'error': 'Вы не можете от(под)писываться сами на себя'},
                status=HTTP_400_BAD_REQUEST)

        if request.method == 'POST':

            _, is_created = Follow.objects.get_or_create(
                user=user,
                author=author
            )

            if not is_created:
                return Response(
                    {'error': 'Вы уже подписаны на этого автора'},
                    status=HTTP_400_BAD_REQUEST
                )

            serializer = SubscribeSirializer(
                author, context={"request": request}
            )

            return Response(serializer.data, status=HTTP_201_CREATED)

        obj = Follow.objects.filter(user=user, author=author)
        if not obj.exists():
            return Response(
                {'error': 'Вы не подписаны на этого автора'},
                status=HTTP_400_BAD_REQUEST)
        obj.delete()

        return Response(status=HTTP_204_NO_CONTENT)

    @action(
            methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """
        Добавляет эндпоинт для списка подписчиков subscriptions.
        """

        user = request.user
        authors = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(authors)

        if pages:
            serializer = SubscribeSirializer(
                pages,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscribeSirializer(
            authors,
            many=True,
            context={'request': request}
        )

        return Response(serializer.data, status=HTTP_200_OK)
