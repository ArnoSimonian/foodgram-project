from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'text',
        'ingredients_list',
        'author',
        'pub_date',
        'favorite_count',
    )
    list_editable = ('name',)
    list_filter = ('name', 'tags', 'author',)
    search_fields = ('name', 'author__username',)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('favorite_count', 'ingredients_list',)

    @admin.display(description='добавления рецепта в избранное')
    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    @admin.display(description='ингредиенты рецепта')
    def ingredients_list(self, recipe):
        items = recipe.recipes_with_ingredients.values_list(
            'ingredient__name', flat=True
        )
        return ', '.join(items)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'color',
        'slug',
    )
    list_editable = ('name', 'slug',)
    search_fields = ('name', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_editable = ('name', 'measurement_unit',)
    list_filter = ('name',)
    search_fields = ('name',)
    inlines = (RecipeIngredientInline,)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
