"""
Views (tasks/views.py)
=======================
A View = a Python function (or class) that:
  1. Receives an HTTP request
  2. Does some logic (get data, process forms, etc.)
  3. Returns an HTTP response (HTML page or redirect)

This file contains TWO types of views:
  A) Regular HTML views (for the web browser)
  B) API views using Django REST Framework (for JSON responses)
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

from .models import Task
from .forms import RegisterForm, TaskForm


# ═══════════════════════════════════════════════════════════════
# SECTION A: HTML VIEWS (Regular web browser views)
# ═══════════════════════════════════════════════════════════════

# ─── AUTHENTICATION VIEWS ────────────────────────────────────────────────────

def register_view(request):
    """
    Handle user registration.
    
    GET  → Show the blank registration form
    POST → Process the form data, create user, log them in
    """
    # If the user is already logged in, send them to the task list
    if request.user.is_authenticated:
        return redirect('task_list')

    if request.method == 'POST':
        # request.POST contains the submitted form data
        form = RegisterForm(request.POST)

        if form.is_valid():
            # Save the new user to the database
            user = form.save()

            # Log the user in immediately after registration
            login(request, user)

            # Add a success flash message
            messages.success(request, f'Account created! Welcome, {user.username}!')

            # Redirect to the task list page
            return redirect('task_list')
        else:
            # Form has errors — they will be shown in the template
            messages.error(request, 'Please fix the errors below.')
    else:
        # GET request — show an empty form
        form = RegisterForm()

    # render() combines a template with data (context) and returns HTML
    return render(request, 'tasks/register.html', {'form': form})


def login_view(request):
    """
    Handle user login.
    
    GET  → Show the login form
    POST → Validate credentials and log the user in
    """
    if request.user.is_authenticated:
        return redirect('task_list')

    if request.method == 'POST':
        # AuthenticationForm is Django's built-in login form
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            # Get the authenticated user object from the form
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('task_list')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'tasks/login.html', {'form': form})


def logout_view(request):
    """
    Log the user out and redirect to login page.
    Only handle POST requests for CSRF security.
    """
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('login')


# ─── TASK VIEWS ──────────────────────────────────────────────────────────────

@login_required  # ← This decorator blocks unauthenticated users!
                  #   If not logged in, redirects to LOGIN_URL from settings.py
def task_list_view(request):
    """
    Show all tasks for the currently logged-in user.
    Also supports filtering by ?filter=completed or ?filter=pending
    """
    # request.user = the currently logged-in User object
    # .tasks = the related_name we set in the ForeignKey
    # This automatically filters to only THIS user's tasks (security!)
    tasks = Task.objects.filter(user=request.user)

    # Optional filtering via URL query parameter: /tasks/?filter=completed
    filter_param = request.GET.get('filter', 'all')
    if filter_param == 'completed':
        tasks = tasks.filter(completed=True)
    elif filter_param == 'pending':
        tasks = tasks.filter(completed=False)

    # Count for display in the template
    total_count = Task.objects.filter(user=request.user).count()
    completed_count = Task.objects.filter(user=request.user, completed=True).count()
    pending_count = total_count - completed_count

    context = {
        'tasks': tasks,
        'filter': filter_param,
        'total_count': total_count,
        'completed_count': completed_count,
        'pending_count': pending_count,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_create_view(request):
    """
    Create a new task.
    
    GET  → Show empty task form
    POST → Save new task to database
    """
    if request.method == 'POST':
        form = TaskForm(request.POST)

        if form.is_valid():
            # commit=False means: create the Task object in memory
            # but DON'T save to database yet (we need to add the user first)
            task = form.save(commit=False)

            # Assign the current logged-in user to this task
            task.user = request.user

            # NOW save to the database (with user set)
            task.save()

            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect('task_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = TaskForm()

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'action': 'Create',  # Used in the template to show "Create Task"
    })


@login_required
def task_update_view(request, pk):
    """
    Update an existing task.
    
    pk = primary key (the task's ID in the URL, e.g. /tasks/5/edit/)
    
    get_object_or_404: tries to find the Task with this id AND this user.
    If not found (wrong id OR wrong user), returns a 404 error.
    This prevents users from editing other people's tasks!
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        # Pass instance=task so the form updates the existing task
        # instead of creating a new one
        form = TaskForm(request.POST, instance=task)

        if form.is_valid():
            form.save()
            messages.success(request, f'Task "{task.title}" updated successfully!')
            return redirect('task_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        # Pre-fill the form with the task's current values
        form = TaskForm(instance=task)

    return render(request, 'tasks/task_form.html', {
        'form': form,
        'action': 'Update',
        'task': task,
    })


@login_required
def task_delete_view(request, pk):
    """
    Delete a task.
    
    GET  → Show confirmation page
    POST → Actually delete the task
    
    Always confirm before deleting! Never delete on a GET request.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        task_title = task.title  # Save title before deletion for the message
        task.delete()
        messages.success(request, f'Task "{task_title}" deleted.')
        return redirect('task_list')

    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle_view(request, pk):
    """
    Toggle the completed status of a task (completed ↔ not completed).
    Only handles POST for security.
    """
    task = get_object_or_404(Task, pk=pk, user=request.user)

    if request.method == 'POST':
        # Flip the boolean value
        task.completed = not task.completed
        task.save()
        status = "completed" if task.completed else "marked as pending"
        messages.success(request, f'Task "{task.title}" {status}.')

    return redirect('task_list')


# ═══════════════════════════════════════════════════════════════
# SECTION B: API VIEWS (Django REST Framework)
# ═══════════════════════════════════════════════════════════════
# These return JSON instead of HTML — used by mobile apps, JS, etc.

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import TaskSerializer


class TaskListAPIView(APIView):
    """
    API endpoint for listing all tasks and creating a new task.
    
    GET  /api/tasks/         → returns list of tasks as JSON
    POST /api/tasks/         → creates a new task from JSON body
    
    APIView is the base class for DRF class-based views.
    It handles authentication, permissions, and content negotiation automatically.
    """
    
    # Only authenticated users can access this view
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Return all tasks belonging to the current user.
        Supports ?filter=completed or ?filter=pending
        """
        tasks = Task.objects.filter(user=request.user)

        # Optional filter
        filter_param = request.query_params.get('filter')
        if filter_param == 'completed':
            tasks = tasks.filter(completed=True)
        elif filter_param == 'pending':
            tasks = tasks.filter(completed=False)

        # TaskSerializer converts Task objects → Python dict → JSON
        # many=True because we're serializing a LIST of tasks
        serializer = TaskSerializer(tasks, many=True)

        return Response(serializer.data)  # Returns JSON automatically

    def post(self, request):
        """
        Create a new task from JSON data in the request body.
        """
        # request.data = parsed JSON body (DRF handles this automatically)
        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid():
            # Save the task, automatically setting the user
            serializer.save(user=request.user)
            # 201 Created is the correct status code for new resources
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        # 400 Bad Request if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    """
    API endpoint for a single task: retrieve, update, or delete.
    
    GET    /api/tasks/<id>/  → get one task
    PUT    /api/tasks/<id>/  → update a task
    DELETE /api/tasks/<id>/  → delete a task
    """
    
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        """
        Helper method: get the task by pk AND user (security check).
        Returns None if not found (caller handles the 404).
        """
        try:
            return Task.objects.get(pk=pk, user=user)
        except Task.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self.get_object(pk, request.user)
        if task is None:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update a task with new data."""
        task = self.get_object(pk, request.user)
        if task is None:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # instance=task tells the serializer to UPDATE, not create
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """Partially update a task (only send the fields you want to change)."""
        task = self.get_object(pk, request.user)
        if task is None:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        # partial=True allows updating only some fields
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a task."""
        task = self.get_object(pk, request.user)
        if task is None:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        task.delete()
        # 204 No Content = success but no body to return
        return Response(status=status.HTTP_204_NO_CONTENT)
