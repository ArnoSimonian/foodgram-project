from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.serializers import UserSubscribeSerializer
from .models import Subscribe, User
from .serializers import SubscribeSerializer, UserSerializer


class UserViewSet(viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @action(methods=["get"],
            permission_classes=(IsAuthenticated,),
            detail=False)
    def me(self, request, *args, **kwargs):
        return Response(self.get_serializer(request.user).data)

    @action(methods=['get'],
            serializer_class=UserSubscribeSerializer,
            permission_classes=(IsAuthenticated,),
            detail=False)
    def subscriptions(self, request):
        subscriptions = (
            User.objects.filter(
                subscribing__user=self.request.user
            )
        )
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            serializer_class=UserSubscribeSerializer,
            permission_classes=(IsAuthenticated,),
            detail=True)
    def subscribe(self, request, pk):
        user = self.request.user
        subscribing = get_object_or_404(User, pk=pk)
        subscription = Subscribe.objects.select_related(
            'user', 'subscribing'
        ).filter(user=user, subscribing=subscribing)

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                data={'user': user.id, 'subscribing': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, subscribing=subscribing)
            serializer = self.get_serializer(
                subscribing, context={'request': self.request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not subscription.exists():
                return Response("Вы не подписаны на этого автора.",
                                status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
