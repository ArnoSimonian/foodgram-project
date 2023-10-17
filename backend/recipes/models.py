from django.core.validators import MinValueValidator, validate_slug
from django.db import models

from users.models import User
from .constants import MAX_RECIPE_VALUE_LENGTH, MAX_TAG_COLOR_LENGTH
from .validators import validate_tag_color, validate_tag_name


class Tag(models.Model):
    name = models.CharField(
        verbose_name='название тега',
        max_length=MAX_RECIPE_VALUE_LENGTH,
        unique=True,
        validators=[validate_tag_name],
    )
    color = models.CharField(
        verbose_name='HEX-цвет тега',
        max_length=MAX_TAG_COLOR_LENGTH,
        unique=True,
        validators=[validate_tag_color],
    )
    slug = models.SlugField(
        verbose_name='слаг тега',
        max_length=MAX_RECIPE_VALUE_LENGTH,
        unique=True,
        validators=[validate_slug],
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
        max_length=MAX_RECIPE_VALUE_LENGTH,
    )
    measurement_unit = models.CharField(
        verbose_name='единица измерения',
        max_length=MAX_RECIPE_VALUE_LENGTH,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_with_measurement_unit',
            ),
        )

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    name = models.CharField(
        verbose_name='название рецепта',
        max_length=MAX_RECIPE_VALUE_LENGTH,
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
    tags = models.ManyToManyField(
        Tag,
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
        related_name='+',
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
        related_name='+',
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
        related_name='+',
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
