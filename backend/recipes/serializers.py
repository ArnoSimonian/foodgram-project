from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.serializers import UserSerializer
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)
from .validators import validate_tag_color, validate_tag_name


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class UserSubscribeSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = int(request.query_params.get('recipes_limit', 0))
        queryset = obj.recipes.all()
        if recipes_limit > 0:
            queryset = queryset[:recipes_limit]
        serializer = RecipeShortSerializer(queryset, many=True, read_only=True)
        return serializer.data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)

    def validate_tag_name(self, value):
        return validate_tag_name(value)

    def validate_tag_color(self, value):
        return validate_tag_color(value)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True, source='ingredient.id')
    name = serializers.CharField(read_only=True, source='ingredient.name')
    measurement_unit = serializers.CharField(
        read_only=True,
        source='ingredient.measurement_unit',
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        read_only=True,
        source='recipes_with_ingredients',
    )
    image = Base64ImageField(use_url=True, max_length=None)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context['request']
        return request.user.is_authenticated and (
            request.user.favorited_by.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return request.user.is_authenticated and (
            request.user.in_shopping_cart_of.filter(recipe=obj).exists()
        )


class RecipeIngredientCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateUpdateSerializer(
        many=True,
        source='recipes_with_ingredients',
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(use_url=True, max_length=None)

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                "Добавьте минимум один ингредиент."
            )
        ingredients_list = [
            ingredient['id'] for ingredient in ingredients
        ]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError(
                "Ингредиенты не могут повторяться."
            )
        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError("Добавьте минимум один тег.")
        if len(tags) != len(set(tag.id for tag in tags)):
            raise serializers.ValidationError("Теги не могут повторяться.")
        return tags

    def validate_image(self, image):
        if not image:
            raise serializers.ValidationError("Добавьте картинку рецепта.")
        return image

    def add_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('recipes_with_ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('recipes_with_ingredients', None)
        if ingredients is None:
            raise serializers.ValidationError(
                "Поле 'ingredients' обязательно для обновления."
            )
        tags = validated_data.pop('tags', None)
        if tags is None:
            raise serializers.ValidationError(
                "Поле 'tags' обязательно для обновления."
            )
        if ingredients:
            RecipeIngredient.objects.select_related(
                'recipe', 'recipes_with_ingredients'
            ).filter(recipe=recipe).delete()
            self.add_ingredients(recipe, ingredients)
        if tags:
            recipe.tags.set(tags)
        recipe = super().update(recipe, validated_data)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return RecipeReadSerializer(instance, context=context).data


class AbstractFavoriteShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('user', 'recipe',)

    def validate(self, data):
        if self.Meta.model.objects.filter(user=data['user'],
                                          recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                "Этот рецепт уже был добавлен ранее."
            )
        if not data['recipe'] and (
            self.context['request'].method == 'DELETE'
        ):
            raise serializers.ValidationError("Этот рецепт не был добавлен.")
        return data

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return RecipeShortSerializer(instance.recipe, context=context).data


class FavoriteSerializer(AbstractFavoriteShoppingCartSerializer):
    class Meta(AbstractFavoriteShoppingCartSerializer.Meta):
        model = Favorite
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe',),
                message="Этот рецепт уже есть в Избранном.",
            ),
        ]


class ShoppingCartSerializer(AbstractFavoriteShoppingCartSerializer):
    class Meta(AbstractFavoriteShoppingCartSerializer.Meta):
        model = ShoppingCart
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe',),
                message="Этот рецепт уже есть в Списке покупок.",
            ),
        ]
