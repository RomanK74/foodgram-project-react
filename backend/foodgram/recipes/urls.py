from django.urls import path
from django.urls.conf import include

from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

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
]
