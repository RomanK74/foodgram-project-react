from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        verbose_name='Название категории',
    )
    color = ColorField(
        default='#000000'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальный идентификатор тега'
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=25,
        verbose_name='Единица измерения',
        blank=False,
    )

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Ингридиент',
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    image = models.ImageField(
        upload_to='media/',
        verbose_name='Фото блюда'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Заполните описание рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipesTags',
        related_name='tags',
        verbose_name='тег'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsInRecipes',
        through_fields=('recipe', 'ingredients'),
        verbose_name='Ингридиент'
    )
    cooking_time = models.PositiveSmallIntegerField(
        help_text='Введите время приготовления в минутах',
        default=1,
        validators=(MinValueValidator(1),),
        verbose_name='Время приготовления',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return (f'({self.name} от {self.author.username})')


class RecipesTags(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег'
    )


class IngredientsInRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Рецепт'
    )
    ingredients = models.ForeignKey(
        Ingredients,
        on_delete=models.PROTECT,
        related_name='ingredients_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингридиента',
        default=1,
        validators=(MinValueValidator(1),),
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Нигридиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredients'), name='unique_ingredient'
            ),
        )

    def __str__(self):
        return self.ingredients.name


class Favorites(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добовления'
    )

    class Meta:
        verbose_name = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='favorite_recipe'
            ),
        )

    def __str__(self):
        return (f'({self.recipe.name} от {self.user.username})')


class IngredientList(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ingredient_list',
        verbose_name='Пользователь'

    )
    date_added = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добовления'
    )

    class Meta:
        verbose_name = 'Списко ингирдиентов'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'), name='unique_list'
            ),
        )
