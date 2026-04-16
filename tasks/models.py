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

    shared_with = models.ManyToManyField(
        User,
        through='SharedTask',
        related_name='shared_tasks',
        blank=True,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    @property
    def is_overdue(self):
        if self.deadline and not self.completed:
            return timezone.now() > self.deadline
        return False


class SharedTask(models.Model):
    """
    Intermediate table for the Task <-> User many-to-many relationship.
    Represents "this task is shared with this user".
    """
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='shares')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_shares')
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('task', 'shared_with')

    def __str__(self):
        return f"{self.task.title} → {self.shared_with.username}"