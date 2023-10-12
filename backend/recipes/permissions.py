from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Кастомный класс разрешений.
    Разрешает только автору рецепта изменять или удалять его.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
            or request.user.is_admin
        )