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
    def get_queryset(self, request):
        qs = self.model._default_manager.get_queryset([0, 1])
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
