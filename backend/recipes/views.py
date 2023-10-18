from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from core.constants import SHOPPING_CART_FILENAME
from .filters import IngredientSearchFilter, RecipeFilter
from .models import Ingredient, Recipe, ShoppingCart, Tag
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
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author').prefetch_related('ingredients__recipe', 'tags')
    serializer_class = RecipeCreateUpdateSerializer
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateUpdateSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post_delete_action(self, serializer_class, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )

        if self.request.method == 'POST':
            serializer = serializer_class(
                data={'user': user.id, 'recipe': recipe.pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if self.request.method == 'DELETE':
            if not object.exists():
                return Response("Рецепт не был добавлен.",
                                status=status.HTTP_400_BAD_REQUEST)
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            detail=True)
    def favorite(self, request, pk):
        return self.post_delete_action(FavoriteSerializer, pk)

    @action(methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,),
            detail=True)
    def shopping_cart(self, request, pk):
        return self.post_delete_action(ShoppingCartSerializer, pk)

    @action(methods=['get'],
            permission_classes=(IsAuthenticated,),
            detail=False)
    def download_shopping_cart(self, request):
        ingredients_in_cart = ShoppingCart.objects.filter(
            user=request.user
        ).values(
            'recipe__ingredients__ingredient__name',
            'recipe__ingredients__ingredient__measurement_unit',
        ).order_by(
            'recipe__ingredients__ingredient__name'
        ).annotate(
            total_amount=Sum('recipe__ingredients__amount')
        )

        shopping_cart = ['Список покупок\n\n']

        for ingredient in ingredients_in_cart:
            ingredient_name = ingredient[
                'recipe__ingredients__ingredient__name'
            ]
            amount = ingredient['total_amount']
            measurement_unit = ingredient[
                'recipe__ingredients__ingredient__measurement_unit'
            ]

            shopping_cart.append(
                f'{ingredient_name}: {amount} {measurement_unit}\n'
            )

        return HttpResponse(
            shopping_cart,
            headers={
                'Content-Type': 'text/plain',
                'Content-Disposition': (
                    f'attachment; filename={SHOPPING_CART_FILENAME}'
                ),
            },
        )
