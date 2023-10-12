import django_filters

from users.models import User
from .models import Ingredient, Recipe, Tag


CHOICES = (
    ('0', 'False'),
    ('1', 'True'),
)

class IngredientFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(django_filters.FilterSet):
    author = django_filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = django_filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = django_filters.ChoiceFilter(
        choices=CHOICES,
        method='filter_is_favorited',
    )
    is_in_shopping_cart = django_filters.ChoiceFilter(
        choices=CHOICES,
        method='filter_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart',)

    def filter_is_favorited(self, queryset, name, value): 
        if value == '1':
            if self.request.user.is_anonymous:
                return queryset.none()
            return queryset.filter(favorite_recipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value == '1':
            if self.request.user.is_anonymous:
                return queryset.none()
            return queryset.filter(is_in_shopping_cart__user=self.request.user)
        return queryset
