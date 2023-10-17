from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
    )
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'subscribing',
    )
