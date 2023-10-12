from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .filters import IngredientFilter, RecipeFilter
from .models import Ingredient, Recipe, Tag
from .permissions import IsAuthorOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateUpdateSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author').prefetch_related('ingredients', 'tags')
    serializer_class = RecipeCreateUpdateSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateUpdateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post_action(self, serializer_class, pk):
        user = self.request.user
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response("Рецепта не существует.",
                            status=status.HTTP_400_BAD_REQUEST)
        object = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )
        if object.exists():
            raise ValidationError("Нельзя добавить рецепт дважды.")
        serializer = serializer_class(
            data={'user': user.id, 'recipe': pk},
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_action(self, serializer_class, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )
        if not object.exists():
            raise ValidationError("Рецепт не был добавлен.")
        object.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            detail=True)
    def favorite(self, request, pk):
        if self.request.method in ('POST'):
            return self.post_action(FavoriteSerializer, pk)
        return self.delete_action(FavoriteSerializer, pk)

    @action(methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            detail=True)
    def shopping_cart(self, request, pk):
        if self.request.method in ('POST'):
            return self.post_action(ShoppingCartSerializer, pk)
        return self.delete_action(ShoppingCartSerializer, pk)

    @action(methods=['get'],
            permission_classes=(IsAuthenticated,),
            detail=False)
    def download_shopping_cart(self, request):
        ingredients_in_cart = Ingredient.objects.filter(
            recipes__is_in_shopping_cart__user=request.user
        ).order_by('name').annotate(
            total_amount=Sum('ingredients_used__amount')
        )

        FILENAME = 'shopping-list.txt'
        TEMPLATE = '{name}: {total_amount} {measurement_unit}\n'

        shopping_cart = (
            TEMPLATE.format(**ingredient.__dict__)
            for ingredient in ingredients_in_cart
        )

        return HttpResponse(
            shopping_cart,
            headers={
                'Content-Type': 'text/plain',
                'Content-Disposition': (
                    f'attachment; filename={FILENAME}'
                ),
            },
        )
