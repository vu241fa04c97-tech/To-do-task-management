from datetime import date

from django.utils.http import urlencode
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, Value, IntegerField

from .models import Task
from .forms import TaskForm


@login_required
def task_list(request):

    today = date.today()

    tasks = Task.objects.filter(user=request.user)

    search = request.GET.get('search')
    status = request.GET.get('status')
    mood = request.GET.get('mood', 'normal')

    if search:
        tasks = tasks.filter(title__icontains=search)

    if status == 'pending':
        tasks = tasks.filter(completed=False)

    elif status == 'completed':
        tasks = tasks.filter(completed=True)

    priority_order = Case(
        When(priority='High', then=Value(1)),
        When(priority='Medium', then=Value(2)),
        When(priority='Low', then=Value(3)),
        default=Value(4),
        output_field=IntegerField()
    )

    if status == 'completed':
        tasks = tasks.order_by('-due_date')

    elif mood == 'energetic':
        tasks = tasks.annotate(priority_rank=priority_order).order_by(
            'completed',
            'due_date',
            'priority_rank'
        )

    elif mood == 'tired':
        tasks = tasks.annotate(priority_rank=priority_order).order_by(
            'completed',
            '-priority_rank',
            'due_date'
        )

    elif mood == 'stressed':
        tasks = tasks.filter(completed=False).annotate(
            priority_rank=priority_order
        ).order_by('due_date', 'priority_rank')[:3]

    else:
        tasks = tasks.order_by('due_date')

    completed_count = Task.objects.filter(
        user=request.user,
        completed=True
    ).count()

    pending_count = Task.objects.filter(
        user=request.user,
        completed=False
    ).count()

    overdue_count = Task.objects.filter(
        user=request.user,
        completed=False,
        due_date__lt=today
    ).count()

    for task in tasks:

        if task.completed:
            task.risk_label = "Completed"
            task.risk_class = "risk-safe"
            task.risk_message = "Task already completed"

        else:
            days_left = (task.due_date - today).days

            if days_left < 0:
                task.risk_label = "High Risk"
                task.risk_class = "risk-high"
                task.risk_message = "Task is already overdue"

            elif days_left <= 2 and task.priority == 'High':
                task.risk_label = "High Risk"
                task.risk_class = "risk-high"
                task.risk_message = "High priority task with very less time"

            elif days_left <= 3 or overdue_count >= 3:
                task.risk_label = "Medium Risk"
                task.risk_class = "risk-medium"
                task.risk_message = "Deadline is close"

            else:
                task.risk_label = "Low Risk"
                task.risk_class = "risk-low"
                task.risk_message = "Likely to complete on time"

    context = {
        'tasks': tasks,
        'completed_count': completed_count,
        'pending_count': pending_count,
        'today': today,
        'selected_mood': mood,
    }

    return render(request, 'tasks/task_list.html', context)


@login_required
def add_task(request):

    if request.method == 'POST':

        form = TaskForm(request.POST)

        if form.is_valid():

            task = form.save(commit=False)

            task.user = request.user

            task.save()

            return redirect('task_list')

    else:

        initial_data = {
            'title': request.GET.get('title', ''),
            'description': request.GET.get('description', '')
        }

        form = TaskForm(initial=initial_data)

    return render(request, 'tasks/add_task.html', {'form': form})


@login_required
def edit_task(request, id):

    task = get_object_or_404(Task, id=id, user=request.user)

    if request.method == 'POST':

        form = TaskForm(request.POST, instance=task)

        if form.is_valid():

            form.save()

            return redirect('task_list')

    else:

        form = TaskForm(instance=task)

    return render(request, 'tasks/edit_task.html', {'form': form})


@login_required
def delete_task(request, id):

    task = get_object_or_404(Task, id=id, user=request.user)

    task.delete()

    return redirect('task_list')


@login_required
def complete_task(request, id):

    task = get_object_or_404(Task, id=id, user=request.user)

    task.completed = True

    task.save()

    return redirect('task_list')


@login_required
def task_dates_api(request):

    tasks = Task.objects.filter(user=request.user)

    date_data = {}

    for task in tasks:

        date_str = task.due_date.strftime('%Y-%m-%d')

        if date_str not in date_data:

            date_data[date_str] = {
                'completed': 0,
                'pending': 0
            }

        if task.completed:

            date_data[date_str]['completed'] += 1

        else:

            date_data[date_str]['pending'] += 1

    return JsonResponse(date_data)


@login_required
def assistant_to_add_task(request):

    title = request.GET.get('title', '')

    description = request.GET.get('description', '')

    query = urlencode({
        'title': title,
        'description': description
    })

    return redirect(f'/add/?{query}')