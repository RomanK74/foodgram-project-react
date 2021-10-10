from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

user_router = DefaultRouter()
user_router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(user_router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
