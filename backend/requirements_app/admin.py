from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.db.models import Count, Max, Q
from .models import CustomUser, ReviewSession, ReviewMessage


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


class ReviewMessageInline(admin.TabularInline):
    model = ReviewMessage
    extra = 0
    readonly_fields = ('role', 'content', 'created_at')
    can_delete = False
    ordering = ('created_at',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ReviewSession)
class ReviewSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'mode', 'status', 'message_count', 'requirement_name', 'created_at')
    list_filter = ('status', 'mode', 'user')
    search_fields = ('user__username', 'requirement__name')
    readonly_fields = ('user', 'requirement', 'mode', 'status', 'form_context', 'generated_description', 'generated_acceptance', 'created_at', 'updated_at')
    inlines = [ReviewMessageInline]
    change_list_template = 'admin/review_session_changelist.html'
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'

    def requirement_name(self, obj):
        return obj.requirement.name if obj.requirement else '-'
    requirement_name.short_description = 'Requirement'

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}

        total_sessions = ReviewSession.objects.count()
        total_messages = ReviewMessage.objects.count()
        unique_users = ReviewSession.objects.values('user').distinct().count()

        status_counts = {row['status']: row['count'] for row in
                         ReviewSession.objects.values('status').annotate(count=Count('id'))}

        confirmed_count = status_counts.get('confirmed', 0)
        confirmation_rate = (confirmed_count / total_sessions * 100) if total_sessions > 0 else 0

        avg_messages = (total_messages / total_sessions) if total_sessions > 0 else 0

        per_user = list(ReviewSession.objects
                        .values('user__username', 'user__role')
                        .annotate(
                            sessions=Count('id', distinct=True),
                            messages=Count('messages', distinct=True),
                            confirmed=Count('id', filter=Q(status='confirmed'), distinct=True),
                            last_activity=Max('created_at')
                        )
                        .order_by('-sessions'))

        extra_context.update({
            'audit_total_sessions': total_sessions,
            'audit_total_messages': total_messages,
            'audit_unique_users': unique_users,
            'audit_status_counts': status_counts,
            'audit_confirmation_rate': confirmation_rate,
            'audit_avg_messages': avg_messages,
            'audit_per_user': per_user,
        })

        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ReviewMessage)
class ReviewMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'content_preview', 'created_at')
    list_filter = ('role',)
    search_fields = ('content', 'session__id')
    readonly_fields = ('session', 'role', 'content', 'created_at')
    ordering = ('-created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'
