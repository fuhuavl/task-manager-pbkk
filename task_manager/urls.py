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
    # Django's built-in admin panel — available at /admin/
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/login/')), 

    # All URLs from our 'tasks' app are included here.
    # '' means no prefix — tasks/urls.py handles everything from root /
    path('', include('tasks.urls')),

    # DRF's built-in login/logout views for the browsable API UI
    # Available at /api-auth/login/ and /api-auth/logout/
    path('api-auth/', include('rest_framework.urls')),
]
