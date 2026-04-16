"""
Tests (tasks/tests.py)
=======================
Django's built-in test framework is based on Python's unittest.

Run all tests with:
  python manage.py test

Run only tasks app tests:
  python manage.py test tasks

These tests demonstrate:
  - TestCase setup (creating test users/tasks)
  - Testing views (authentication redirects, status codes)
  - Testing models (object creation, string representation)
  - Testing the API (DRF endpoints)
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Task


class TaskModelTest(TestCase):
    """Tests for the Task model."""

    def setUp(self):
        """setUp runs BEFORE each test method. Create reusable test data here."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.task = Task.objects.create(
            user=self.user,
            title='Test Task',
            description='A test description',
            completed=False
        )

    def test_task_creation(self):
        """Task should be created with correct fields."""
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.user, self.user)
        self.assertFalse(self.task.completed)

    def test_task_str(self):
        """__str__ should return 'title (username)'."""
        expected = f"Test Task ({self.user.username})"
        self.assertEqual(str(self.task), expected)

    def test_task_default_not_completed(self):
        """New tasks should not be completed by default."""
        task = Task.objects.create(user=self.user, title='Another Task')
        self.assertFalse(task.completed)


class TaskViewTest(TestCase):
    """Tests for HTML views."""

    def setUp(self):
        self.client = Client()  # Django test client (simulates a browser)
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.task = Task.objects.create(
            user=self.user,
            title='My Task',
            completed=False
        )

    def test_task_list_requires_login(self):
        """Unauthenticated users should be redirected to login."""
        response = self.client.get(reverse('task_list'))
        # 302 = redirect; should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_task_list_authenticated(self):
        """Logged-in users should see the task list."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Task')

    def test_user_cannot_see_other_users_tasks(self):
        """A user should only see their own tasks."""
        # Create another user with their own task
        other_user = User.objects.create_user(username='other', password='pass123')
        Task.objects.create(user=other_user, title='Secret Task')

        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('task_list'))

        # testuser should see their task but NOT the other user's task
        self.assertContains(response, 'My Task')
        self.assertNotContains(response, 'Secret Task')

    def test_create_task(self):
        """POST to task_create should create a new task."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('task_create'), {
            'title': 'New Task',
            'description': 'New description',
            'completed': False,
        })
        # Should redirect after successful creation
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='New Task').exists())


class TaskAPITest(TestCase):
    """Tests for DRF API endpoints."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        self.task = Task.objects.create(
            user=self.user,
            title='API Task',
            completed=False
        )

    def test_api_requires_authentication(self):
        """Unauthenticated API requests should return 403."""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, 403)

    def test_api_list_tasks(self):
        """Authenticated GET /api/tasks/ should return task list."""
        self.client.login(username='apiuser', password='apipass123')
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'API Task')

    def test_api_create_task(self):
        """POST /api/tasks/ should create a task."""
        self.client.login(username='apiuser', password='apipass123')
        response = self.client.post(
            '/api/tasks/',
            {'title': 'Via API', 'description': '', 'completed': False},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Task.objects.filter(title='Via API').exists())

    def test_api_delete_task(self):
        """DELETE /api/tasks/<id>/ should remove the task."""
        self.client.login(username='apiuser', password='apipass123')
        response = self.client.delete(f'/api/tasks/{self.task.pk}/')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())
