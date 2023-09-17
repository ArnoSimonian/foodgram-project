from djoser.views import UserViewSet
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import User
from .serializers import UserCreateSerializer, UserSerializer


class UserViewSet(UserViewSet):
    #http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (IsAuthenticated,)
    # lookup_field = 'username'
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('username',)

    # @action(methods=['GET', 'PATCH'],
    #         detail=False,
    #         permission_classes=(IsAuthenticated,),
    #         url_path='me')