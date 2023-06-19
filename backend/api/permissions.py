from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Пермишн дает фулл-доступ админу, остальным только чтение.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_staff
        )


class IsAdminOrIsAuthorOrReadOnly(BasePermission):
    """
    Пермишн регулирует доступ к рецептам.

    Админ получает полный доступ, включая доступ к объектам
    Автор рецепта - полный доступ, включая доступ к своему рецепту
    Авторизованный пользователь - просмотр списка и создание обекта
    Анонимный пользователь - только просмотр.
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or request.user.is_staff
            or obj.author == request.user
        )
