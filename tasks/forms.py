from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Task


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class TaskForm(forms.ModelForm):
    share_with = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter username to share with (optional)',
        }),
        label='Share with user (username)',
        help_text='Type a username to share this task with them.',
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'What needs to be done?',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Add details (optional)...',
                'rows': 4,
            }),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local',
            }, format='%Y-%m-%dT%H:%M'),
        }
        labels = {
            'title': 'Task Title',
            'description': 'Description (optional)',
            'deadline': 'Deadline (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.deadline:
            self.initial['deadline'] = self.instance.deadline.strftime('%Y-%m-%dT%H:%M')
        if self.instance and self.instance.pk:
            existing = self.instance.shared_with.values_list('username', flat=True)
            self.initial['share_with'] = ', '.join(existing)

    def clean_title(self):
        title = self.cleaned_data.get('title').strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        return title

    def clean_share_with(self):
        """
        Validate the share_with field.
        Accepts comma-separated usernames: "john, jane, bob"
        """
        raw = self.cleaned_data.get('share_with', '')
        if not raw.strip():
            return []

        usernames = [u.strip() for u in raw.split(',') if u.strip()]
        valid_users = []
        errors = []

        for username in usernames:
            try:
                user = User.objects.get(username=username)
                valid_users.append(user)
            except User.DoesNotExist:
                errors.append(f'User "{username}" does not exist.')

        if errors:
            raise forms.ValidationError(errors)

        return valid_users