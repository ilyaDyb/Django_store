from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm

from users.models import User


def email_no(value):
    try:
        user_mail = User.objects.get(email=value)
        raise forms.ValidationError("Такая почта уже существует")
    except User.DoesNotExist:
        pass


class UserRegistrationForm(UserCreationForm):
    username = forms.CharField()
    email = forms.EmailField(validators=[email_no])
    password1 = forms.CharField()
    password2 = forms.CharField()
    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]



class UserLoginForm(AuthenticationForm):
    class Meta:
        model = User
        fields = [
            'username', 'password'
        ]


class ProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "image",
            "first_name",
            "last_name",
            "username",
            "email",)

    image = forms.ImageField(required=False)
    first_name = forms.CharField()
    last_name = forms.CharField()
    username = forms.CharField()
    email = forms.CharField()