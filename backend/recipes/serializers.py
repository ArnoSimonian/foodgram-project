import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import Subscribe
from users.serializers import CustomUserSerializer
from .models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )
        validators = [
            UniqueTogetherValidator(
                queryset=Subscribe.objects.all(),
                fields=('user', 'subscribing'),
                message="Нельзя подписаться на автора дважды."
            )
        ]

    def get_recipes(self, obj):
        request = self.context['request']
        recipes_limit = int(request.query_params.get('recipes_limit', 0))
        queryset = obj.recipes.all()
        if recipes_limit > 0:
            queryset = queryset[:recipes_limit]
        serializer = RecipeShortSerializer(queryset, many=True, read_only=True)
        return serializer.data

    def validate(self, data):
        if self.context['request'].method == 'POST' and (
            self.context['request'].user.pk == self.context['view'].kwargs.get(
                'user_id')
        ):
                raise serializers.ValidationError(
                    "Нельзя подписаться на самого себя.")
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        many=True,
        read_only=True,
        source='ingredients_used',
    )
    image = serializers.URLField(source='image.url')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

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
            request.user.favorited_by.filter(favorite_recipe=obj).exists()
        )
        
    def get_is_in_shopping_cart(self, obj):
        request = self.context['request']
        return request.user.is_authenticated and (
            request.user.in_shopping_cart_of.filter(is_in_shopping_cart=obj).exists()
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super(Base64ImageField, self).to_internal_value(data)


class RecipeIngredientCreateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientCreateUpdateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField()

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

    def add_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient.get('id'),
                amount=ingredient.get('amount'),
            )
            for ingredient in ingredients
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        recipe = super().update(recipe, validated_data)
        if ingredients:
            recipe.ingredients.clear()
            self.add_ingredients(recipe, ingredients)
        if tags:
            recipe.tags.set(tags)
        recipe.save()
        return recipe

    def to_representation(self, instance):
        context = {'request': self.context['request']}
        return RecipeReadSerializer(instance, context=context).data


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = RecipeShortSerializer(
        read_only=True,
        source='favorite_recipe',
    )

    class Meta:
        model = Favorite
        fields = 'recipe'
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message="Этот рецепт уже есть в Избранном."
            )
        ]


class ShoppingCartSerializer(serializers.ModelSerializer):
    recipe = RecipeShortSerializer(
        read_only=True,
        source='is_in_shopping_cart'
    )

    class Meta:
        model = ShoppingCart
        fields = 'recipe'
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCart.objects.all(),
                fields=('user', 'recipe'),
                message="Этот рецепт уже есть в Списке покупок."
            )
        ]
