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
    class Meta:
        model = Task
        # completed is removed here — toggled via checkbox on the list page instead
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
            # datetime-local is the HTML input type for date+time pickers
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
        # Format existing deadline value correctly for the datetime-local input
        if self.instance and self.instance.deadline:
            self.initial['deadline'] = self.instance.deadline.strftime('%Y-%m-%dT%H:%M')

    def clean_title(self):
        title = self.cleaned_data.get('title').strip()
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters long.")
        return title