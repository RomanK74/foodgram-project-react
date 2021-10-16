from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.serializers import ValidationError

from users.models import User
from users.serializers import UserDetailSerializer

from .models import (Favorite, Ingredient, IngredientInRecipe, IngredientList,
                     Recipe, Tag)

INGREDIENT_VALIDATION_ERROR = 'Добавте хотябы один ингредиент!'
UNIQUE_INGREDIENT_ERROR = 'Ингредиент уже в рецепте!'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class IngredientsInRecipesSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredients.id')
    name = serializers.ReadOnlyField(source='ingredients.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredients.measurement_unit')

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class IngredientsInRecipesPostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientInRecipe
        fields = (
            'id',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    author = UserDetailSerializer()
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
            'cooking_time'
        )

    def get_ingredients(self, obj):
        queryset = IngredientInRecipe.objects.filter(recipe=obj)
        return IngredientsInRecipesSerializer(queryset, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe_id=obj.id
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return IngredientList.objects.filter(
            user=request.user, recipe=obj
        ).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    ingredients = IngredientsInRecipesPostSerializer(many=True)
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'image',
            'ingredients',
            'tags',
            'author',
            'name',
            'text',
            'cooking_time'
        )

    def validate(self, data):
        if 'ingredients' not in self.initial_data['ingredientsS']:
            raise ValidationError(INGREDIENT_VALIDATION_ERROR)
        ingredients = self.initial_data.get('ingredients')
        ingredients_list = len(ingredients)
        ingredient_set = len(
            set([ingredient['id'] for ingredient in ingredients])
        )
        if ingredients_list > ingredient_set:
            raise ValidationError(UNIQUE_INGREDIENT_ERROR)
        return data

    def add_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            item = ingredient['id']
            amount = ingredient['amount']
            IngredientInRecipe.objects.create(
                ingredients=item,
                recipe=recipe,
                amount=amount
            )

    def create(self, validate_data):
        tags = validate_data.pop('tags')
        ingredient = validate_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user, **validate_data
        )
        recipe.tags.set(tags)
        self.add_ingredients(ingredient, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = self.context['request'].data['tags']
        instance.tags.set(tags)
        instance.name = validated_data.get('name', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        if 'ingredients' in self.initial_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.add_ingredients(ingredients, instance)
        instance.save()
        return instance


class FavoriteRecipesSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
    )

    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe'
        )


class IngredientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientList
        fields = '__all__'
