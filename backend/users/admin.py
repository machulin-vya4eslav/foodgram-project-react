from django.contrib import admin

from .models import User, Follow


class UserAdmin(admin.ModelAdmin):
    """
    Настройки обображения в админке объектов User.
    """

    list_display = ('pk', 'first_name', 'last_name', 'username', 'email') 
    list_filter = ('username', 'email')
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """
    Настройки обображения в админке объектов Follow.
    """

    list_display = ('user', 'author',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)

admin.site.register(Follow, FollowAdmin)
