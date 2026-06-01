from django.urls import path
from . import views

urlpatterns = [

    path('register/', views.register_view, name='register'),

    path('login/', views.login_view, name='login'),

    path('forgot-password/', views.forgot_password_view, name='forgot_password'),

    path('reset-password/', views.reset_password_view, name='reset_password'),

    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile_view, name='profile'),

    path('edit-profile/', views.edit_profile_view, name='edit_profile'),

    path('delete-account/', views.delete_account_view, name='delete_account'),

]