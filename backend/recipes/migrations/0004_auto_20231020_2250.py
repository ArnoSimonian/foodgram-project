# Generated by Django 3.2.16 on 2023-10-20 22:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_auto_20231019_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200, validators=[django.core.validators.RegexValidator(message='Поле name может содержать только русские и латинские буквы и пробел.', regex='^[A-Za-zа-яА-Я ]+$')], verbose_name='ингредиент'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(max_length=200, validators=[django.core.validators.RegexValidator(message='Поле name может содержать только русские и латинские буквы и пробел.', regex='^[A-Za-zа-яА-Я ]+$')], verbose_name='название рецепта'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(max_length=7, unique=True, validators=[django.core.validators.RegexValidator(message="Поле color должно содержать латинские буквы 'a-f/A-F' и/или цифры, начинаться с символа '#' и содержать не более 7 символов.", regex='^#([0-9a-fA-F]{3}){1,2}\\Z')], verbose_name='HEX-цвет тега'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, unique=True, validators=[django.core.validators.RegexValidator(message='Поле name может содержать только русские и латинские буквы и пробел.', regex='^[A-Za-zа-яА-Я ]+$')], verbose_name='название тега'),
        ),
    ]
