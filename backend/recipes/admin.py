from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     RecipeTag, ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
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
    )
    list_editable = ('name',)
    list_filter = ('tags', 'ingredients',)
    search_fields = ('name', 'author__username',)
    inlines = (RecipeIngredientInline, RecipeTagInline,)
    readonly_fields = ('ingredients_list',)

    @admin.display(description='ингредиенты')
    def ingredients_list(self, recipe):
        items = recipe.ingredients.values_list('name', flat=True)
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
    inlines = (RecipeTagInline,)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'name',
        'measurement_unit',
    )
    list_editable = ('name', 'measurement_unit',)
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
