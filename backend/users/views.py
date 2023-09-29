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
from .models import User, Subscribe
from .serializers import UserSubscribeSerializer

# User = get_user_model()


class UserViewSet(djoser_views.UserViewSet):
    http_method_names = ['get', 'post']
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_permissions(self):
        if self.action == 'me':
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()


class SubscribeViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'delete']
    serializer_class=UserSubscribeSerializer
    permission_classes=(IsAuthenticated,)

    @action(methods=['get'],
            detail=False)
    def subscriptions(self, request):
        subscriptions = (
            User.objects.filter(subscribing__subscriber=self.request.user)
            .annotate(last_recipe_date=Max('recipes__pub_date'))
            .order_by(F('last_recipe_date').desc(nulls_last=True))
        )
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['post'],
            detail=True)
    def subscribe(self, request, id):
        subscriber = request.user
        subscribing = get_object_or_404(User, pk=id)
        if Subscribe.objects.filter(
            subscriber=subscriber, subscribing=subscribing
        ).exists():
            raise ValidationError("Нельзя подписаться на автора дважды.")
        if subscriber == subscribing:
            raise ValidationError("Нельзя подписаться на самого себя.")
        Subscribe.objects.create(subscriber=subscriber, subscribing=subscribing)
        serializer = self.get_serializer(subscribing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['delete'],
            detail=True)
    def subscribe_delete(self, request, id):
        subscription = Subscribe.objects.filter(
            subscriber=request.user,
            subscribing=get_object_or_404(User, pk=id),
        )
        if not subscription.exists():
            raise ValidationError("Подписки не существует.")
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
