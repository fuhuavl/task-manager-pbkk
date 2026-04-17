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
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.utils import timezone
import calendar
from datetime import date

from .models import Task, SharedTask
from .forms import RegisterForm, TaskForm


# ─── AUTH VIEWS ──────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created! Welcome, {user.username}!')
            return redirect('task_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()
    return render(request, 'tasks/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('task_list')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
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
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('login')


# ─── TASK VIEWS ──────────────────────────────────────────────────────────────

@login_required
def task_list_view(request):
    own_tasks = Task.objects.filter(user=request.user)
    shared_tasks = Task.objects.filter(shared_with=request.user)

    filter_param = request.GET.get('filter', 'all')
    if filter_param == 'completed':
        own_tasks = own_tasks.filter(completed=True)
        shared_tasks = shared_tasks.filter(completed=True)
    elif filter_param == 'pending':
        own_tasks = own_tasks.filter(completed=False)
        shared_tasks = shared_tasks.filter(completed=False)

    tasks = (own_tasks | shared_tasks).distinct().order_by('-created_at')

    total_count = own_tasks.count() + shared_tasks.count()
    completed_count = own_tasks.filter(completed=True).count() + shared_tasks.filter(completed=True).count()
    pending_count = total_count - completed_count

    context = {
        'tasks': tasks,
        'filter': filter_param,
        'total_count': total_count,
        'completed_count': completed_count,
        'pending_count': pending_count,
    }
    return render(request, 'tasks/task_list.html', context)


def _handle_share(task, share_users, current_user):
    """
    Helper: update sharing for a task.
    Removes old shares and adds new ones, excluding the task owner.
    """
    # Remove all existing shares
    SharedTask.objects.filter(task=task).delete()
    # Add new shares (can't share with yourself)
    for user in share_users:
        if user != current_user:
            SharedTask.objects.create(task=task, shared_with=user)


@login_required
def task_create_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            # Handle sharing
            share_users = form.cleaned_data.get('share_with', [])
            _handle_share(task, share_users, request.user)
            if share_users:
                names = ', '.join(u.username for u in share_users)
                messages.success(request, f'Task created and shared with: {names}')
            else:
                messages.success(request, f'Task "{task.title}" created!')
            return redirect('task_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Create'})


@login_required
def task_update_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            share_users = form.cleaned_data.get('share_with', [])
            _handle_share(task, share_users, request.user)
            messages.success(request, f'Task "{task.title}" updated!')
            return redirect('task_list')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'action': 'Update', 'task': task})


@login_required
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        title = task.title
        task.delete()
        messages.success(request, f'Task "{title}" deleted.')
        return redirect('task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})


@login_required
def task_toggle_view(request, pk):
    # Allow toggling own tasks OR tasks shared with you
    task = Task.objects.filter(pk=pk).filter(
        user=request.user
    ).first() or Task.objects.filter(pk=pk, shared_with=request.user).first()

    if not task:
        messages.error(request, 'Task not found.')
        return redirect('task_list')

    if request.method == 'POST':
        task.completed = not task.completed
        task.save()
        status = "completed" if task.completed else "marked as pending"
        messages.success(request, f'Task "{task.title}" {status}.')
        next_url = request.POST.get('next')
        if next_url and next_url.startswith('#'):
            referrer = request.META.get('HTTP_REFERER')
            if referrer:
                return redirect(referrer + next_url)
            return redirect('task_list')
        return redirect(next_url or request.META.get('HTTP_REFERER', 'task_list'))
    return redirect(request.META.get('HTTP_REFERER', 'task_list'))


# ─── CALENDAR VIEW ───────────────────────────────────────────────────────────

@login_required
def calendar_view(request):
    # Get year/month from URL params, default to current month
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Navigate prev/next month
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Get all tasks with deadlines in this month that belong to
    # the user (own tasks OR shared with them)
    own_tasks = Task.objects.filter(
        user=request.user,
        deadline__year=year,
        deadline__month=month,
    )
    shared_tasks = Task.objects.filter(
        shared_with=request.user,
        deadline__year=year,
        deadline__month=month,
    )
    # Combine into one list
    all_tasks = list(own_tasks) + list(shared_tasks)

    # Build a dict: {day_number: [task, task, ...]}
    tasks_by_day = {}
    for task in all_tasks:
        day = task.deadline.day
        if day not in tasks_by_day:
            tasks_by_day[day] = []
        tasks_by_day[day].append(task)

    # Build calendar grid
    # calendar.monthcalendar returns list of weeks,
    # each week is [Mon, Tue, Wed, Thu, Fri, Sat, Sun] with 0 for empty days
    cal = calendar.monthcalendar(year, month)

    # Previous and next month links
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    context = {
        'year': year,
        'month': month,
        'month_name': calendar.month_name[month],
        'cal': cal,
        'tasks_by_day': tasks_by_day,
        'today': today,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'day_names': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    }
    return render(request, 'tasks/calendar.html', context)


# ─── API VIEWS ───────────────────────────────────────────────────────────────

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import TaskSerializer


class TaskListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(user=request.user)
        filter_param = request.query_params.get('filter')
        if filter_param == 'completed':
            tasks = tasks.filter(completed=True)
        elif filter_param == 'pending':
            tasks = tasks.filter(completed=False)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Task.objects.get(pk=pk, user=user)
        except Task.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        return Response(TaskSerializer(task).data)

    def put(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        task = self.get_object(pk, request.user)
        if not task:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)