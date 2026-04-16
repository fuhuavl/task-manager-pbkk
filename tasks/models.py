from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def is_overdue(self):
        """Returns True if the task has a deadline that has already passed."""
        if self.deadline and not self.completed:
            return timezone.now() > self.deadline
        return False