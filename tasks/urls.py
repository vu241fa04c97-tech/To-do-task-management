from django.urls import path
from . import views

urlpatterns = [

    path('', views.task_list, name='task_list'),

    path('add/', views.add_task, name='add_task'),

    path('edit/<int:id>/', views.edit_task, name='edit_task'),

    path('delete/<int:id>/', views.delete_task, name='delete_task'),

    path('complete/<int:id>/', views.complete_task, name='complete_task'),

    path('task-dates/', views.task_dates_api, name='task_dates_api'),

    path(
        'assistant-to-add/',
        views.assistant_to_add_task,
        name='assistant_to_add_task'
    ),

]