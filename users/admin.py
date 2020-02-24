from django.contrib import admin

from users.models import User, Diplomats, War


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Diplomats)
class DiplomatsAdmin(admin.ModelAdmin):
    pass

@admin.register(War)
class WarAdmin(admin.ModelAdmin):
    pass