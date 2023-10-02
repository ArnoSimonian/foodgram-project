from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .filters import RecipeFilter
from .models import Ingredient, Recipe, RecipeIngredient, RecipeTag, Tag
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
    filter_backends = (filters.SearchFilter,)
    #filterset_class = IngredientFilter
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return RecipeCreateUpdateSerializer
        return RecipeReadSerializer

    def get_queryset(self):
        return (
            Recipe.objects.select_related('author')
            .prefetch_related(Prefetch('recipeingredient_set',
                                       queryset=RecipeIngredient.objects
                                       .select_related('ingredient')))
                                       .prefetch_related(Prefetch('recipetag_set',
                                       queryset=RecipeTag.objects
                                       .select_related('tag')))
                                       .all()
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post_delete(self, serializer_class, pk):
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user, recipe=recipe
        )

        if self.request.method == 'POST':
            if object.exists():
                raise ValidationError("Нельзя добавить рецепт дважды.")
            serializer = serializer_class(
                data={'user': user.id, 'recipe': pk},
                context={'request': self.request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif self.request.method == 'DELETE':
            if not object.exists():
                raise ValidationError("Рецепт не был добавлен.")
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk):
        return self.post_delete(FavoriteSerializer, pk)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk):
        return self.post_delete(ShoppingCartSerializer, pk)
    