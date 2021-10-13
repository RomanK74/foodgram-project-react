# Generated by Django 3.2.8 on 2021-10-08 08:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsinrecipes',
            name='ingredients',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_ingredients',
                to='recipes.ingredients', verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='ingredientsinrecipes',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_ingredients',
                to='recipes.recipe'),
        ),
    ]
