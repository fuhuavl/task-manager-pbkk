# ✅ Task Manager — Django Learning Project

A complete To-Do List web application built with Django and Django REST Framework.
Designed for learning all core Django concepts in one project.

---

## 📁 Project Structure

```
task_manager_project/        ← Root folder (your working directory)
│
├── manage.py                ← Django's command-line utility (run this for everything)
│
├── requirements.txt         ← Python packages to install
│
├── db.sqlite3               ← SQLite database file (auto-created after migrate)
│
├── static/                  ← Project-level static files
│   └── css/
│       └── style.css        ← Main stylesheet
│
├── templates/               ← Project-level templates
│   └── base.html            ← Master layout template (all pages extend this)
│
├── task_manager/            ← The Django PROJECT package
│   ├── __init__.py          ← Makes this folder a Python package
│   ├── settings.py          ← All configuration (DB, apps, middleware, etc.)
│   ├── urls.py              ← Root URL router
│   ├── wsgi.py              ← For production servers (WSGI interface)
│   └── asgi.py              ← For async servers (ASGI interface)
│
└── tasks/                   ← The 'tasks' Django APP
    ├── __init__.py
    ├── models.py            ← Database models (Task)
    ├── views.py             ← Request handlers (HTML views + API views)
    ├── urls.py              ← App-level URL patterns
    ├── forms.py             ← Django forms (RegisterForm, TaskForm)
    ├── serializers.py       ← DRF serializers (Task ↔ JSON)
    ├── admin.py             ← Admin panel configuration
    ├── apps.py              ← App configuration class
    ├── migrations/          ← Database migration files
    │   ├── __init__.py
    │   └── 0001_initial.py  ← Creates the Task table
    └── templates/
        └── tasks/           ← App templates (namespaced in subfolder)
            ├── login.html
            ├── register.html
            ├── task_list.html
            ├── task_form.html
            └── task_confirm_delete.html
```

### Project vs App — What's the Difference?

| Concept | Folder | Purpose |
|---------|--------|---------|
| **Project** | `task_manager/` | Global config, root URLs, settings |
| **App** | `tasks/` | One feature area: models, views, URLs |

A Django project can have MANY apps (e.g. `tasks`, `blog`, `shop`).
Each app is self-contained and reusable.

---

## 🚀 Setup & Run (Step by Step)

### 1. Create a virtual environment
```bash
python -m venv venv

# Activate it:
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run migrations (create the database tables)
```bash
python manage.py makemigrations
python manage.py migrate
```

What these do:
- `makemigrations` — reads models.py and creates migration files (like a blueprint)
- `migrate` — reads migration files and creates/alters actual database tables

### 4. Create a superuser (for the admin panel)
```bash
python manage.py createsuperuser
# Follow the prompts: username, email, password
```

### 5. Start the development server
```bash
python manage.py runserver
```

Open your browser at: **http://127.0.0.1:8000**

---

## 🌐 URL Map

| URL | View | Description |
|-----|------|-------------|
| `/register/` | register_view | Create a new account |
| `/login/` | login_view | Log in |
| `/logout/` | logout_view | Log out |
| `/tasks/` | task_list_view | View all your tasks |
| `/tasks/create/` | task_create_view | Create a new task |
| `/tasks/<id>/edit/` | task_update_view | Edit a task |
| `/tasks/<id>/delete/` | task_delete_view | Delete a task |
| `/tasks/<id>/toggle/` | task_toggle_view | Toggle completed |
| `/admin/` | Django Admin | Admin dashboard |
| `/api/tasks/` | TaskListAPIView | API: list + create |
| `/api/tasks/<id>/` | TaskDetailAPIView | API: get/update/delete |
| `/api-auth/` | DRF Auth | API login/logout |

---

## 🔌 REST API Usage

The API returns JSON. You must be logged in (session auth) to use it.

### Get all tasks
```
GET /api/tasks/
GET /api/tasks/?filter=completed
GET /api/tasks/?filter=pending
```

### Create a task
```
POST /api/tasks/
Content-Type: application/json

{
    "title": "Learn Django",
    "description": "Build a task manager app",
    "completed": false
}
```

### Get one task
```
GET /api/tasks/1/
```

### Update a task
```
PUT /api/tasks/1/
Content-Type: application/json

{
    "title": "Learn Django",
    "description": "Updated description",
    "completed": true
}
```

### Partially update (only some fields)
```
PATCH /api/tasks/1/
Content-Type: application/json

{ "completed": true }
```

### Delete a task
```
DELETE /api/tasks/1/
```

---

## 🔐 Security Features

1. **CSRF Protection** — All forms include `{% csrf_token %}` to prevent cross-site attacks
2. **Login Required** — `@login_required` decorator blocks unauthenticated users
3. **Data Isolation** — All queries filter by `user=request.user` so users only see their own tasks
4. **Password Hashing** — Django hashes passwords using PBKDF2 (never stored in plain text)
5. **get_object_or_404** — Returns 404 (not 403) if a user tries to access another user's task
6. **DRF Permissions** — `IsAuthenticated` class blocks unauthenticated API access

---

## 🧠 Key Django Concepts Covered

| Concept | Where |
|---------|-------|
| Project structure | Entire project layout |
| Models & ORM | `tasks/models.py` |
| Migrations | `tasks/migrations/` |
| Forms & Validation | `tasks/forms.py` |
| Function-Based Views | `tasks/views.py` (HTML views) |
| Class-Based API Views | `tasks/views.py` (API section) |
| URL routing | `task_manager/urls.py` + `tasks/urls.py` |
| Template inheritance | `base.html` + child templates |
| Template tags & filters | `{% url %}`, `{% csrf_token %}`, `|date:` |
| Static files | `static/css/style.css` |
| Authentication | `login`, `logout`, `@login_required` |
| Django Admin | `tasks/admin.py` |
| Django REST Framework | `tasks/serializers.py` + API views |
| Flash messages | `messages.success()` / `{% if messages %}` |

---

## 🧪 Useful Commands

```bash
# Open the interactive Django shell
python manage.py shell

# Inside the shell, try:
from tasks.models import Task
from django.contrib.auth.models import User

# Get all tasks
Task.objects.all()

# Get tasks for a specific user
user = User.objects.get(username='john')
user.tasks.all()

# Create a task manually
Task.objects.create(user=user, title='Shell task', description='Created from shell')

# See the SQL for a queryset
print(Task.objects.filter(user=user).query)
```

---

## 📝 Notes for University Assignment

This project demonstrates:
- ✅ Django project/app architecture
- ✅ ORM models with relationships (ForeignKey)
- ✅ Database migrations
- ✅ ModelForms with validation
- ✅ Function-based views (auth + tasks)
- ✅ Class-based API views (DRF)
- ✅ Template inheritance and Django template language
- ✅ Static file configuration
- ✅ Built-in authentication system
- ✅ URL namespacing
- ✅ REST API with serializers
- ✅ Security best practices (CSRF, login_required, per-user data)
