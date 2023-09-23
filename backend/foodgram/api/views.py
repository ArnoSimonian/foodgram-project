from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from users.models import User
from .pagination import LimitPageNumberPagination
from .serializers import UserCreateSerializer, UserSerializer

# User = get_user_model()


class UserViewSet(UserViewSet):
    http_method_names = ['get', 'post']
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # queryset = User.objects.all()
    # serializer_class = UserCreateSerializer
    # pagination_class = LimitPageNumberPagination

    # def get_serializer_class(self):
    #     if self.action in ['list', 'retrieve']:
    #         return UserSerializer
    #     return UserCreateSerializer

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()
