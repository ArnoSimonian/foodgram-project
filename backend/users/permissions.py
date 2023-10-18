from rest_framework import permissions


class CurrentUserOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """
    Кастомный класс разрешений.
    Разрешает неавторизованному пользователю просмотр профиля
    любого пользователя за исключением эндпоинта 'me'.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS and view.action != 'me'
            or request.user.is_authenticated
        )
