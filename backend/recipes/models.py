from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .utils import (INGREDIENT_NAME_LENGTH, MEASUREMENT_UNIT_LENGTH,
                    RECIPE_NAME_LENGTH, TAG_COLOR_LENGTH, TAG_NAME_LENGTH,
                    TAG_SLUG_LENGTH)
from .validators import validate_tag_color, validate_tag_slug


class Tag(models.Model):
    name = models.CharField(
        verbose_name='название тега',
        max_length=TAG_NAME_LENGTH,
        unique=True,
    )
    color = models.CharField(
        verbose_name='HEX-цвет тега',
        max_length=TAG_COLOR_LENGTH,
        unique=True,
        validators=[validate_tag_color],
    )
    slug = models.SlugField(
        verbose_name='слаг тега',
        max_length=TAG_SLUG_LENGTH,
        unique=True,
        validators=[validate_tag_slug],
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='ингредиент',
        max_length=INGREDIENT_NAME_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=MEASUREMENT_UNIT_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='название рецепта',
        max_length=RECIPE_NAME_LENGTH,
    )
    text = models.TextField('описание')
    author = models.ForeignKey(
        User,
        verbose_name='автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    pub_date = models.DateTimeField(
        'дата публикации',
        auto_now_add=True,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='cписок ингредиентов',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='список тегов',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления (в минутах)',
        validators=[MinValueValidator(
            1,
            message="Время приготовления не может быть менее 1 минуты.",
        )],
    )
    image = models.ImageField(
        verbose_name='картинка рецепта',
        upload_to='recipes/',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='recipes_with_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredients_used',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='количество ингридиента',
        validators=[MinValueValidator(
            1,
            message="Количество должно быть не менее единицы.",
        )],
    )

    class Meta:
        verbose_name = 'рецепт-ингредиент'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient',
            ),
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: {self.ingredient.name}, '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        on_delete=models.CASCADE,
        related_name='recipes_with_tags',
    )
    tag = models.ForeignKey(
        Tag,
        verbose_name='тег',
        on_delete=models.CASCADE,
        related_name='tags_used',
    )

    class Meta:
        verbose_name = 'рецепт-тег'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'tag'],
                name='unique_recipe_tag',
            ),
        ]

    def __str__(self):
        return f'{self.recipe.name}: {self.tag.name}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепты в избранном',
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_recipe',
            ),
        )

    def __str__(self):
        return f'{self.user.username}: {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        on_delete=models.CASCADE,
        related_name='in_shopping_cart_of',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепты в списке покупок',
        on_delete=models.CASCADE,
        related_name='is_in_shopping_cart',
    )

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'списки покупок'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_shopping_cart',
            ),
        )

    def __str__(self):
        return f'{self.user.username}: {self.recipe.name}'
