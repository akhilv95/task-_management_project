from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Task

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin interface"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'assigned_admin', 'is_active')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role', 'assigned_admin')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role', 'assigned_admin')}),
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Task admin interface"""
    
    list_display = ('title', 'assigned_to', 'assigned_by', 'status', 'due_date', 'worked_hours', 'created_at')
    list_filter = ('status', 'created_at', 'due_date', 'assigned_by')
    search_fields = ('title', 'description', 'assigned_to__username', 'assigned_by__username')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Task Information', {
            'fields': ('title', 'description', 'assigned_to', 'assigned_by', 'due_date')
        }),
        ('Status & Progress', {
            'fields': ('status', 'completion_report', 'worked_hours', 'completed_at')
        }),
    )
    
    readonly_fields = ('completed_at', 'created_at', 'updated_at')