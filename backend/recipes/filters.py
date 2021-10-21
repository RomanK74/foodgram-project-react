from django_filters import rest_framework as filters

from .models import Ingredient, Recipe, Tag


class RecipeFilters(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        label='Tags',
        to_field_name="slug",
    )

    is_favorited = filters.BooleanFilter(
        method='get_favorited',
        label='Favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_favorited(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(favorited_by__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return queryset.filter(ingredient_list__user=user)
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', method='start_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def start_name(self, queryset, slug, name):
        return queryset.filter(name__startswith=name)
