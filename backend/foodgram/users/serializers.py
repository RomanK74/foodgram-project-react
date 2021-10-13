from django.contrib.auth import password_validation
from djoser.serializers import (SetPasswordSerializer, UserCreateSerializer,
                                UserSerializer)
from rest_framework import serializers

from recipes.models import Recipe

from .models import Subscriptions, User

WRONG_PASSWORD = 'Неправильный пароль, попробуйте еще раз.'


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserDetailSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )
        lookup_field = 'username'

    def get_is_subscribed(self, obj):
        return Subscriptions.objects.filter(
            user__id=self.context['request'].user.id,
            author=obj
        ).exists()


class ChangePasswordSerializer(SetPasswordSerializer):
    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if not is_password_valid:
            raise WRONG_PASSWORD
        return value

    def validate(self, data):
        password_validation.validate_password(
            data['new_password'], self.context['request'].user
        )
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class SubscribeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Subscriptions
        fields = (
            'user',
            'author'
        )


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeAuthorSerializer(UserDetailSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserDetailSerializer.Meta):
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:(int(recipes_limit))]
        else:
            recipes = obj.recipes.all()
        context = {'request': request}
        return SubscribeRecipeSerializer(
            recipes,
            many=True,
            context=context
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
