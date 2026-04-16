"""
Migration File: 0001_initial.py
================================
Migrations are Django's way of tracking and applying changes to your database schema.

When you run `python manage.py makemigrations`, Django:
  1. Reads your models.py
  2. Compares it to the last migration
  3. Generates this file describing what changed

When you run `python manage.py migrate`, Django:
  1. Reads all migration files
  2. Runs any that haven't been applied yet
  3. Updates the database schema accordingly

Think of migrations like Git commits — but for your database structure.
Each file records ONE set of changes. You should commit them to version control!

Common commands:
  python manage.py makemigrations        # detect model changes, create migration file
  python manage.py migrate               # apply pending migrations to DB
  python manage.py showmigrations        # list all migrations and their status
  python manage.py sqlmigrate tasks 0001 # show the raw SQL this migration runs
"""

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    # This is the FIRST migration (no dependencies on other task migrations)
    initial = True

    # dependencies: other migrations that must run BEFORE this one
    dependencies = [
        # We depend on auth because our Task model has a ForeignKey to User
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    # operations: the list of changes to apply to the database
    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                # Auto-created primary key (id column)
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Short title of the task (max 200 characters)', max_length=200)),
                ('description', models.TextField(blank=True, help_text='Detailed description of the task (optional)')),
                ('completed', models.BooleanField(default=False, help_text='Has this task been completed?')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='When this task was created (set automatically)')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='When this task was last updated (set automatically)')),
                # ForeignKey creates a user_id column referencing auth_user.id
                ('user', models.ForeignKey(
                    help_text='The user who owns this task',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tasks',
                    to=settings.AUTH_USER_MODEL
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
