from django.urls import path
from django.urls.conf import include
from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    DownloadIngredientsList
)
from rest_framework.routers import DefaultRouter

recipes_router = DefaultRouter()
recipes_router.register('tags', TagViewSet, basename='tags')
recipes_router.register(
    'ingredients',
    IngredientViewSet,
    basename='ingredients'
)
recipes_router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(recipes_router.urls)),
    path('recipes/download_shopping_cart/',
         DownloadIngredientsList.as_view(),
         name='download_shopping_cart')
]
