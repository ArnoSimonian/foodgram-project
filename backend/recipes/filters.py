import django_filters

from rest_framework import filters

from .models import Recipe, Tag


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'


class RecipeFilter(django_filters.FilterSet):
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited',
    )
    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            recipe_ids = set(
                self.request.user.favorited_by.values_list(
                    'recipe_id', flat=True
                )
            )
            return queryset.filter(id__in=recipe_ids)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            recipe_ids = set(
                self.request.user.in_shopping_cart_of.values_list(
                    'recipe_id', flat=True
                )
            )
            return queryset.filter(id__in=recipe_ids)
        return queryset
