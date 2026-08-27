from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('Role & Profile', {'fields': ('role', 'phone', 'profile_image')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'email', 'first_name', 'last_name', 'phone', 'is_active')
        }),
    )

    @staticmethod
    def _is_owner_user(user):
        return bool(
            getattr(user, 'is_authenticated', False)
            and getattr(user, 'is_active', False)
            and (getattr(user, 'is_superuser', False) or getattr(user, 'is_owner', False))
        )

    def has_module_permission(self, request):
        return self._is_owner_user(request.user)

    def has_view_permission(self, request, obj=None):
        if self._is_owner_user(request.user):
            return True
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        if self._is_owner_user(request.user):
            return True
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        if self._is_owner_user(request.user):
            return True
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self._is_owner_user(request.user):
            return True
        return super().has_delete_permission(request, obj)
