
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
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomListPagination

    @action(
            methods=['post', 'delete'],
            detail=True,
            permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id):
        user = request.user
        author = User.objects.get(id=id)

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

    @action(
            methods=['get'],
            detail=False,
            permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
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

    def get_serializer_context(self):

        result = {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

        user = self.request.user

        if user.is_authenticated:
            following = User.objects.filter(following__user=user)
            result['following'] = following

        return result
