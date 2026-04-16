"""
App-Level URL Configuration (tasks/urls.py)
============================================
This file maps URL patterns to view functions for the 'tasks' app.

URL pattern format:
  path('url-pattern/', view_function, name='url_name')

The 'name' allows us to use {% url 'url_name' %} in templates
instead of hardcoding URLs — makes refactoring easier!

These URLs are INCLUDED in task_manager/urls.py (the project-level urls.py).
"""

from django.urls import path
from . import views

# ── HTML page URLs ──────────────────────────────────────────────
# These return rendered HTML pages for the browser

urlpatterns = [
    # ── Authentication ──
    # /register/  → register_view
    path('register/', views.register_view, name='register'),
    
    # /login/     → login_view
    path('login/', views.login_view, name='login'),
    
    # /logout/    → logout_view
    path('logout/', views.logout_view, name='logout'),

    # ── Tasks ──
    # /tasks/             → task_list_view (show all tasks)
    path('tasks/', views.task_list_view, name='task_list'),
    
    # /tasks/create/      → task_create_view (form to create task)
    path('tasks/create/', views.task_create_view, name='task_create'),
    
    # /tasks/5/edit/      → task_update_view for task with id=5
    # <int:pk> is a URL parameter — Django captures the integer and passes it to the view
    path('tasks/<int:pk>/edit/', views.task_update_view, name='task_update'),
    
    # /tasks/5/delete/    → task_delete_view for task with id=5
    path('tasks/<int:pk>/delete/', views.task_delete_view, name='task_delete'),
    
    # /tasks/5/toggle/    → toggle completed status for task with id=5
    path('tasks/<int:pk>/toggle/', views.task_toggle_view, name='task_toggle'),

    # ── API URLs (Django REST Framework) ──
    # These return JSON instead of HTML

    # /api/tasks/         → GET list, POST create
    path('api/tasks/', views.TaskListAPIView.as_view(), name='api_task_list'),
    
    # /api/tasks/5/       → GET detail, PUT update, DELETE delete
    path('api/tasks/<int:pk>/', views.TaskDetailAPIView.as_view(), name='api_task_detail'),
]
