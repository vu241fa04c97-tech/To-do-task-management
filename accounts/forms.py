from django import forms
from django.contrib.auth.models import User
from .models import UserProfile


class RegisterForm(forms.Form):

    username = forms.CharField(max_length=100)

    email = forms.EmailField()

    mobile = forms.CharField(max_length=15)

    password = forms.CharField(widget=forms.PasswordInput)

    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):

        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")

        if UserProfile.objects.filter(mobile=mobile).exists():
            raise forms.ValidationError("Mobile number already exists")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class PersonalDetailsForm(forms.Form):

    existing_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Existing Password"
    )

    name = forms.CharField(max_length=100, required=False)

    username = forms.CharField(max_length=100)

    email = forms.EmailField()

    mobile = forms.CharField(max_length=15)

    gender = forms.ChoiceField(
        choices=[
            ('', 'Select Gender'),
            ('Male', 'Male'),
            ('Female', 'Female'),
            ('Other', 'Other'),
        ],
        required=False
    )

    designation = forms.CharField(max_length=100, required=False)

    profile_photo = forms.ImageField(required=False)

    new_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="New Password"
    )

    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput,
        required=False,
        label="Confirm New Password"
    )

    def __init__(self, user, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.user = user

    def clean(self):

        cleaned_data = super().clean()

        existing_password = cleaned_data.get('existing_password')
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        mobile = cleaned_data.get('mobile')
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if not self.user.check_password(existing_password):
            raise forms.ValidationError("Existing password is incorrect")

        if User.objects.exclude(id=self.user.id).filter(username=username).exists():
            raise forms.ValidationError("Username already exists")

        if User.objects.exclude(id=self.user.id).filter(email=email).exists():
            raise forms.ValidationError("Email already exists")

        if UserProfile.objects.exclude(user=self.user).filter(mobile=mobile).exists():
            raise forms.ValidationError("Mobile number already exists")

        if new_password or confirm_new_password:
            if new_password != confirm_new_password:
                raise forms.ValidationError("New passwords do not match")

        return cleaned_data


class DeleteAccountForm(forms.Form):

    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.user = user

    def clean_password(self):

        password = self.cleaned_data.get('password')

        if not self.user.check_password(password):
            raise forms.ValidationError("Password is incorrect")

        return password