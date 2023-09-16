from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Subscribe, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'password',
        'role'
    )
    list_editable = ('role',)
    search_fields = ('username', 'email',)
    list_filter = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(Subscribe)
