from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):

    CATEGORY_CHOICES = [

    ('Work', 'Work'),

    ('Personal', 'Personal'),

    ('Study', 'Study'),

    ('Shopping', 'Shopping'),

    ]
   
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    due_date = models.DateField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title