"""
Project-Level URL Configuration (task_manager/urls.py)
=======================================================
This is the MAIN router of the entire project.
Every URL request hits this file first.

Think of it like a switchboard:
  - /admin/  → goes to Django admin
  - /api/    → goes to DRF (REST API)
  - everything else → goes to our 'tasks' app
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/')), 
    path('', include('tasks.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
