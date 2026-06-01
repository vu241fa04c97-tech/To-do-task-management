from django import forms
from .models import Task


class TaskForm(forms.ModelForm):

    class Meta:
        model = Task

        fields = [
            'title',
            'description',
            'category',
            'priority',
            'due_date',
            'completed'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task title'
            }),

            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter task description',
                'rows': 4
            }),

            'category': forms.Select(attrs={
                'class': 'form-control'
            }),

            'priority': forms.Select(attrs={
                'class': 'form-control'
            }),

            'due_date': forms.TextInput(attrs={
                'class': 'form-control datepicker',
                'placeholder': 'YYYY-MM-DD'
            }),

            'completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }