from django_filters.rest_framework import filters
from rest_framework.filters import SearchFilter

from .models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            recipe_ids = list(
                self.request.user.favorited_by.values_list(
                    'recipe_id', flat=True
                )
            )
            return queryset.filter(id__in=recipe_ids)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            recipe_ids = list(
                self.request.user.in_shopping_cart_of.values_list(
                    'recipe_id', flat=True
                )
            )
            return queryset.filter(id__in=recipe_ids)
        return queryset
