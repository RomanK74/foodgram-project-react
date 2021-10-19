from django_filters import rest_framework as filters

from .models import Ingredient, Recipe


class RecipeFilters(filters.FilterSet):
    tas = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Tags'
    )

    is_favorited = filters.BooleanFilter(
        method='get_is_favorited'
    )
    is_in_ingredient_list = filters.BooleanFilter(
        method='get_is_in_ingredient_list'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_ingredient_list')

    def get_is_favorited(self, queyset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorites__user=user)
        return Recipe.objects.all()

    def get_is_in_ingredient_list(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(ingredient_list__user=user)
        return Recipe.objects.all()


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name',)
