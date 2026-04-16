"""
App Configuration (tasks/apps.py)
====================================
Every Django app has an AppConfig class.
Django uses it to set up the app (signals, app label, etc.)

It's registered in INSTALLED_APPS as 'tasks' (short form)
or 'tasks.apps.TasksConfig' (full form — same result).
"""

from django.apps import AppConfig


class TasksConfig(AppConfig):
    # The default type for auto-created primary key fields
    default_auto_field = 'django.db.models.BigAutoField'
    
    # The name must match the folder name of the app
    name = 'tasks'
    
    # Human-readable name (shows in admin)
    verbose_name = 'Task Manager'
