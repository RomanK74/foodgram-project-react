from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .filters import IngredientFilter, RecipeFilters
from .models import (
    Favorite, Ingredient, IngredientInRecipe, IngredientList, Recipe, Tag,
)
from .paginator import RecipesPagination
from .serializers import (
    FavoriteRecipesSerializer, IngredientListSerializer, IngredientSerializer,
    RecipePostSerializer, RecipeSerializer, TagSerializer,
)

FAVORITE_CREATE_MESSAGE = 'Рецепт успешно добавлен в избранное'
FAVORITE_DELETE_ERROR_MESSAGE = 'Этого речепта небыло в избранном'
FAVORITE_DELETE_MESSAGE = 'Рецепт удалён из избранного'
SHOPPING_CART_ADD_MESSAGE = 'Рецепт успешно добавлен в корзину'
SHOPPING_CART_ERROR_MESSAGE = 'Рецепта нет в списке покупок'
SHOPPING_CART_DELETE_MESSAGE = 'Рецепт успешно удален из списка покупок'


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filter_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilters
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = RecipesPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipePostSerializer

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        serializer = FavoriteRecipesSerializer(
            data={
                'recipe': pk,
                'user': request.user.id
            }
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'GET':
            serializer.save()
            return Response(
                {'status': FAVORITE_CREATE_MESSAGE},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(
                {'status': FAVORITE_DELETE_MESSAGE},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=['GET', 'DELETE'],
        permission_classes=(permissions.IsAuthenticated, )
    )
    def shopping_cart(self, request, pk):
        serializer = IngredientListSerializer(
            data={
                'recipe': pk,
                'user': request.user.id
            }
        )
        serializer.is_valid(raise_exception=True)
        if request.method == 'GET':
            serializer.save()
            return Response(
                {'status': SHOPPING_CART_ADD_MESSAGE},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            recipe = self.get_object()
            IngredientList.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            return Response(
                {'status': SHOPPING_CART_DELETE_MESSAGE},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        buying_list = {}
        shopping_cart = IngredientInRecipe.objects.filter(
            recipe__ingredient_list__user=request.user
        ).values_list(
            'amount',
            'ingredients__name',
            'ingredients__measurement_unit',
            named=True
        ).order_by('id')
        for ingredient in shopping_cart:
            measurement_unit = ingredient.ingredients__measurement_unit
            name = ingredient.ingredients__name
            amount = ingredient.amount

            if name not in buying_list:
                buying_list[name] = {
                    'amount': amount,
                    'measurement_unit': measurement_unit,
                }
            else:
                buying_list[name]['amount'] = (buying_list[name]['amount']
                                               + amount)
        wishlist = []
        for item in buying_list:
            wishlist.append(f'{item} - {buying_list[item]["amount"]}'
                            f' {buying_list[item]["measurement_unit"]} \n')

        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
