from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    Custom form for creating new users. Extends Django's default UserCreationForm
    to include the custom 'role' field and ensure secure password hashing.
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'role')


class CustomUserChangeForm(UserChangeForm):
    """
    Custom form for editing existing users. Includes the custom 'role' field.
    """
    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = ('username', 'role', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Fieldsets for editing an existing user
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'first_name', 'last_name')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    
    # Fieldsets specifically for the "Add User" creation form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'role', 'password1', 'password2'),
        }),
    )
