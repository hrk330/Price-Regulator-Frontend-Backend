from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_type', 'device_id', 'ip_address', 'last_activity', 'is_active', 'created_at']
    list_filter = ['session_type', 'is_active', 'created_at', 'last_activity']
    search_fields = ['user__email', 'user__name', 'device_id', 'ip_address']
    readonly_fields = ['id', 'access_token', 'refresh_token', 'created_at', 'last_activity']
    ordering = ['-last_activity']
    actions = ['deactivate_sessions', 'activate_sessions']
    
    fieldsets = (
        (None, {'fields': ('user', 'session_type', 'device_id', 'is_active')}),
        ('Session Details', {'fields': ('access_token', 'refresh_token', 'expires_at')}),
        ('Client Info', {'fields': ('ip_address', 'user_agent')}),
        ('Timestamps', {'fields': ('created_at', 'last_activity')}),
    )
    
    def deactivate_sessions(self, request, queryset):
        """Deactivate selected sessions."""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} session(s) were successfully deactivated. Users will be logged out on their next request.',
            level='SUCCESS'
        )
    deactivate_sessions.short_description = "Deactivate selected sessions"
    
    def activate_sessions(self, request, queryset):
        """Activate selected sessions."""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} session(s) were successfully activated.',
            level='SUCCESS'
        )
    activate_sessions.short_description = "Activate selected sessions"
    
    def save_model(self, request, obj, form, change):
        """Override save to show warning when deactivating a session."""
        if change and 'is_active' in form.changed_data:
            # If is_active was changed to False
            if not obj.is_active:
                self.message_user(
                    request,
                    f'Session for {obj.user.email} has been deactivated. The user will be logged out on their next request.',
                    level='WARNING'
                )
        super().save_model(request, obj, form, change)
