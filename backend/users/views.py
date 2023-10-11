from django.db.models import F, Max
from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from recipes.serializers import UserSubscribeSerializer
from users.serializers import CustomUserSerializer
from .models import User, Subscribe

# User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    @action(methods=['get'],
            serializer_class=UserSubscribeSerializer,
            permission_classes=(IsAuthenticated,),
            detail=False)
    def subscriptions(self, request):
        subscriptions = (
            User.objects.filter(
                subscribing__user=self.request.user).annotate(
                    last_recipe_date=Max('recipes__pub_date')).order_by(
                        F('last_recipe_date').desc(nulls_last=True))
        )
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'],
            serializer_class=UserSubscribeSerializer,
            permission_classes=(IsAuthenticated,),
            detail=True)
    def subscribe(self, request, id):
        user = self.request.user
        subscribing = get_object_or_404(User, pk=id)
        subscription = Subscribe.objects.select_related('user', 'subscribing').filter(
            user=user, subscribing=subscribing,
        )

        if request.method == 'POST':
            if subscription.exists():
                raise ValidationError("Нельзя подписаться на автора дважды.")
            if user == subscribing:
                raise ValidationError("Нельзя подписаться на самого себя.")
            Subscribe.objects.create(user=user, subscribing=subscribing)
            serializer = self.get_serializer(subscribing)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not subscription.exists():
                raise ValidationError("Вы не подписаны на этого автора.")
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
