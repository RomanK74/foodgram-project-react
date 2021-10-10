from django.conf import settings
from django.contrib.auth import password_validation
from rest_framework import serializers
from djoser.serializers import (UserCreateSerializer, UserSerializer,
                                SetPasswordSerializer)

from .models import Subscribtion, User
from recipes.models import Recipe


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
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
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribtion.objects.get(
            subscriber=request.user, author=obj).exists()


class ChangePasswordSerializer(SetPasswordSerializer):
    def validate_current_password(self, value):
        is_password_valid = self.context['request'].user.check_password(value)
        if not is_password_valid:
            raise 'Неправильный пароль!'
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
    class Meta:
        model = Subscribtion
        fields = (
            'user',
            'author'
        )

    def validate(self, attrs):
        if self.context['request'].user == attrs['author']:
            raise serializers.ValidationError(
                'Вы не можете подписатся на себя.'
            )
        return attrs


class SubscribersRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeAuthorSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
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
        recipes = obj.recipes.all()[:settings.RECIPES_LIMIT]
        request = self.context.get('request')
        return SubscribersRecipeSerializer(
            recipes,
            many=True,
            context={'request': request}
        ).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
