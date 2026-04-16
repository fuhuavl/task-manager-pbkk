"""
Admin Registration (tasks/admin.py)
=====================================
Register our models with Django's admin site.

The admin site is a built-in Django feature that auto-generates
a CRUD interface for your models. Access it at /admin/

Very useful for:
  - Browsing and editing data during development
  - Quick debugging
  - Admin-only operations
"""

from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Customize how Task objects appear in the admin panel.
    """
    
    # list_display: columns shown in the task list table
    list_display = ['title', 'user', 'completed', 'created_at']
    
    # list_filter: adds filter sidebar on the right
    list_filter = ['completed', 'created_at', 'user']
    
    # search_fields: enables search bar, searches these fields
    search_fields = ['title', 'description', 'user__username']
    
    # readonly_fields: these fields can't be edited in the admin
    readonly_fields = ['created_at', 'updated_at']
    
    # ordering: default sort in the admin list view
    ordering = ['-created_at']
    
    # list_per_page: how many items per page in the list view
    list_per_page = 20
