from django.contrib import admin

from recipes.models import (
    Favorite, Ingredient, IngredientInRecipe, IngredientList, Recipe, Tag,
)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'author', 'name', 'pub_date')
    exclude = ("ingredients",)
    search_fields = ('author', 'name', 'tags')
    readonly_fields = ('pub_date', )
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('tags',)
    empty_value_display = '-пусто-'


@admin.register(IngredientInRecipe)
class IngredientsInRecipesAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredients', 'amount')


class IngredientItemAdmin(admin.StackedInline):
    model = Recipe.ingredients.through
    extra = 0


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'
    prepopulated_fields = {'slug': ('name', )}


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(IngredientList)
class IngredientListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user', 'date_added')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'user', 'date_added')
    search_fields = ('user', 'recipe')
    empty_value_display = '-пусто-'
