#from django.contrib.auth import get_user_model
from django.db.models import F, Max
from django.shortcuts import get_object_or_404
from djoser import views as djoser_views
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

#from api.pagination import LimitPageNumberPagination
from recipes.serializers import UserSubscribeSerializer
from .models import User, Subscribe

# User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    http_method_names = ['get', 'post', 'delete']
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
        user = request.user
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

        if request.method == 'DELETE':
            if not subscription.exists():
                raise ValidationError("Вы не подписаны на этого автора.")
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
