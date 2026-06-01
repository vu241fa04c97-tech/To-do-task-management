import random
from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

from tasks.models import Task
from .forms import RegisterForm, PersonalDetailsForm, DeleteAccountForm
from .models import UserProfile


def register_view(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )

            UserProfile.objects.create(
                user=user,
                mobile=form.cleaned_data['mobile']
            )

            login(request, user)

            messages.info(request, "Please update your profile details.")

            return redirect('profile')

        else:

            messages.error(request, "Username, email, or mobile already exists.")

    else:

        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):

    if request.method == 'POST':

        login_input = request.POST.get('login_input')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=login_input,
            password=password
        )

        if user is None:

            users = User.objects.filter(email=login_input)

            if users.count() == 1:

                user_obj = users.first()

                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password
                )

            elif users.count() > 1:

                messages.error(
                    request,
                    "Multiple accounts found with this email. Please login using username."
                )

                return render(request, 'accounts/login.html')

        if user is not None:

            login(request, user)

            return redirect('task_list')

        else:

            messages.error(request, "Invalid username/email or password.")

    return render(request, 'accounts/login.html')


def forgot_password_view(request):

    if request.method == 'POST':

        email = request.POST.get('email')

        users = User.objects.filter(email=email)

        if not users.exists():

            messages.error(request, "Email is not registered.")

            return redirect('forgot_password')

        if users.count() > 1:

            messages.error(
                request,
                "Multiple accounts found with this email. Please contact admin or login using username."
            )

            return redirect('forgot_password')

        user = users.first()

        otp = str(random.randint(100000, 999999))

        request.session['reset_user_id'] = user.id

        request.session['reset_otp'] = otp

        send_mail(
            'Password Reset OTP',
            f'Your OTP for password reset is {otp}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False
        )

        messages.success(request, "OTP sent to your registered email.")

        return redirect('reset_password')

    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request):

    if request.method == 'POST':

        entered_otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        saved_otp = request.session.get('reset_otp')
        user_id = request.session.get('reset_user_id')

        if entered_otp != saved_otp:

            messages.error(request, "Invalid OTP.")

            return redirect('reset_password')

        if new_password != confirm_password:

            messages.error(request, "Passwords do not match.")

            return redirect('reset_password')

        user = User.objects.get(id=user_id)

        user.set_password(new_password)

        user.save()

        request.session.pop('reset_otp', None)
        request.session.pop('reset_user_id', None)

        messages.success(request, "Password updated successfully. Please login.")

        return redirect('login')

    return render(request, 'accounts/reset_password.html')


def logout_view(request):

    logout(request)

    return redirect('login')


def get_or_create_user_profile(user):

    try:

        profile = UserProfile.objects.get(user=user)

    except UserProfile.DoesNotExist:

        profile = UserProfile.objects.create(
            user=user,
            mobile=f'temp_{user.id}'
        )

    return profile


def clean_mobile_for_display(mobile):

    if not mobile:

        return ""

    if mobile == "Not added":

        return ""

    if mobile.startswith("temp_"):

        return ""

    return mobile


@login_required
def profile_view(request):

    profile = get_or_create_user_profile(request.user)

    tasks = Task.objects.filter(user=request.user)

    total_tasks = tasks.count()

    completed_tasks = tasks.filter(completed=True).count()

    pending_tasks = tasks.filter(completed=False).count()

    overdue_tasks = tasks.filter(
        completed=False,
        due_date__lt=date.today()
    ).count()

    if total_tasks == 0:

        score = 0

    else:

        completion_score = (completed_tasks / total_tasks) * 70

        early_completed = tasks.filter(
            completed=True,
            due_date__gte=date.today()
        ).count()

        early_score = (early_completed / total_tasks) * 30

        overdue_penalty = overdue_tasks * 5

        score = round(completion_score + early_score - overdue_penalty)

        if score < 0:
            score = 0

        if score > 100:
            score = 100

    if score >= 81:

        level = "Master Planner"
        badge = "🏆"

    elif score >= 61:

        level = "Achiever"
        badge = "🎯"

    elif score >= 41:

        level = "Performer"
        badge = "⚡"

    elif score >= 21:

        level = "Consistent"
        badge = "🔥"

    else:

        level = "Beginner"
        badge = "🌱"

    achievements = []

    if completed_tasks >= 1:
        achievements.append("First Task Completed")

    if completed_tasks >= 5:
        achievements.append("5 Tasks Completed")

    if completed_tasks >= 10:
        achievements.append("10 Tasks Champion")

    if overdue_tasks == 0 and total_tasks > 0:
        achievements.append("Deadline Hero")

    if score >= 80:
        achievements.append("Productivity Master")

    context = {
        'profile': profile,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'pending_tasks': pending_tasks,
        'overdue_tasks': overdue_tasks,
        'score': score,
        'level': level,
        'badge': badge,
        'achievements': achievements,
    }

    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):

    profile = get_or_create_user_profile(request.user)

    if request.method == 'POST':

        form = PersonalDetailsForm(
            request.user,
            request.POST,
            request.FILES
        )

        if form.is_valid():

            request.user.username = form.cleaned_data['username']
            request.user.email = form.cleaned_data['email']

            new_password = form.cleaned_data.get('new_password')

            if new_password:

                request.user.set_password(new_password)

            request.user.save()

            profile.name = form.cleaned_data['name']
            profile.mobile = form.cleaned_data['mobile']
            profile.gender = form.cleaned_data['gender']
            profile.designation = form.cleaned_data['designation']

            if form.cleaned_data.get('profile_photo'):

                profile.profile_photo = form.cleaned_data['profile_photo']

            profile.profile_updated = True

            profile.save()

            if new_password:

                logout(request)

                messages.success(
                    request,
                    "Password changed successfully. Please login again."
                )

                return redirect('login')

            messages.success(request, "Profile updated successfully.")

            return redirect('profile')

    else:

        mobile_value = clean_mobile_for_display(profile.mobile)

        form = PersonalDetailsForm(
            request.user,
            initial={
                'name': profile.name,
                'username': request.user.username,
                'email': request.user.email,
                'mobile': mobile_value,
                'gender': profile.gender,
                'designation': profile.designation,
            }
        )

    return render(request, 'accounts/edit_profile.html', {'form': form})


@login_required
def delete_account_view(request):

    if request.method == 'POST':

        form = DeleteAccountForm(request.user, request.POST)

        if form.is_valid():

            user = request.user

            logout(request)

            user.delete()

            messages.success(request, "Account deleted successfully.")

            return redirect('login')

    else:

        form = DeleteAccountForm(request.user)

    return render(request, 'accounts/delete_account.html', {'form': form})