# Generated by Django 3.2.16 on 2023-09-30 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_auto_20230930_1025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients_used', to='recipes.ingredient', verbose_name='ингредиент'),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes_with_ingredients', to='recipes.recipe', verbose_name='рецепт'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes_with_tags', to='recipes.recipe', verbose_name='рецепт'),
        ),
        migrations.AlterField(
            model_name='recipetag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags_used', to='recipes.tag', verbose_name='тег'),
        ),
    ]