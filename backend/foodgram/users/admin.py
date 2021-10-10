from django.contrib import admin
from .models import User, Subscribtion


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'role')
    search_fields = ('username', 'email')
    list_filter = ('role',)
    empty_value_display = '-пусто-'


@admin.register(Subscribtion)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    search_fields = ('user',)
    empty_value_display = '-пусто-'
