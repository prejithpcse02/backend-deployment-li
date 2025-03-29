from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from django.utils.translation import gettext_lazy as _

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'nickname')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email  # Set username to be the same as email
        if commit:
            user.save()
        return user

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'nickname', 'is_active', 'is_staff', 'is_superuser')

class CustomUserAdmin(UserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    
    # Customize which fields to display in the admin interface
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("nickname",)}),  # Removed first_name and last_name
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    
    # Fields for adding a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nickname", "password1", "password2"),
            },
        ),
    )
    
    # List display shows these columns in the admin user list
    list_display = ("email", "nickname", "is_staff", "is_active")
    
    # List of fields to search by
    search_fields = ("email", "nickname")
    
    # Order users by these fields
    ordering = ("email",)

# Register the User model with the custom admin
admin.site.register(User, CustomUserAdmin)
