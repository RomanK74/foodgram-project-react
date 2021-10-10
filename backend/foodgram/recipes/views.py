from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.views import APIView
from rest_framework import permissions, status

from .filters import RecipeFilters, IngredientFilter
from .paginator import RecipesPagination
from .models import (
    Tag,
    Ingredients,
    Recipe,
    Favorites,
    IngredientsInRecipes,
    IngredientList,
)
from .serializers import (
    TagSerializer,
    IngredientsSerializer,
    RecipeSerializer,
    RecipePostSerializer,
    FavoriteRecipesSerializer,
    IngredientListSerializer,
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientsSerializer
    queryset = Ingredients.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    filter_class = IngredientFilter
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend, )
    filter_class = RecipeFilters
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    pagination_class = RecipesPagination

    def get_queryset(self):
        queryset = Recipe.objects.all()
        is_favorited = self.request.query_params.get('is_favorited')
        favorited = Favorites.objects.filter(user=self.request.user.id)
        if is_favorited == 'true':
            queryset = queryset.filter(favorites__in=favorited)
        else:
            queryset = queryset.exclude(favorites__in=favorited)
        return queryset.all()

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
                {'status': 'Рецепт успешно добавлен в избранное'},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            recipe = self.get_object()
            deleted_objects = Favorites.objects.filter(
                user=request.user,
                recipe=recipe
            ).delete()
            if deleted_objects is None:
                raise 'Этого речепта небыло в избранном'
            return Response(
                {'status': 'Рецепт удалён из избранного'},
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
                {'status': 'Рецепт успешно добавлен в корзину'},
                status=status.HTTP_201_CREATED
            )
        if request.method == 'DELETE':
            recipe = self.get_object()
            deleted_recipe = IngredientList.objects.filter(
                user=request.user,
                recipe=recipe
            )
            if deleted_recipe is None:
                raise 'Рецепта нет в списке покупок'
            return Response(
                {'status': 'Рецепт успешно удален из списка покупок'},
                status=status.HTTP_204_NO_CONTENT
            )


class DownloadIngredientsList(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        buying_list = {}
        ingredients = IngredientsInRecipes.objects.filter(
            recipe__shopping_cart__user=request.user).values_list(
            'ingredients__name', 'amount', 'ingredients__measurement_unit')
        ingredients = ingredients.values(
            'ingredients__name', 'ingredients__measurement_unit'
        ).annotate(total=Sum('amount'))
        for ingredient in ingredients:
            amount = ingredient['total']
            name = ingredient['ingredients__name']
            measurement_unit = ingredient['ingredients__measurement_unit']
            buying_list[name] = {'measurement_unit': measurement_unit,
                                 'amount': amount}
        wishlist = []
        for item in buying_list:
            wishlist.append(f'{item} - {buying_list[item]["amount"]} '
                            f'{buying_list[item]["measurements_unit"]} \n')

        response = HttpResponse(wishlist, 'Content-Type: text/plain')
        response['Content-Disposition'] = 'attachment; filename="wishlist.txt"'
        return response
