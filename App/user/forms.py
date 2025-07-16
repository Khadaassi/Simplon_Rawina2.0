from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label=_("Username"),
        max_length=30,
        required=True,
        widget=forms.TextInput(
            attrs={"placeholder": _("Enter your username"), "class": "form-control"}
        ),
    )

    email = forms.EmailField(
        label=_("Email"),
        max_length=254,
        required=True,
        widget=forms.EmailInput(
            attrs={"placeholder": _("Enter your email address"), "class": "form-control"}
        ),
    )

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
                "placeholder": _("Enter your password"),
                "class": "form-control",
            }
        ),
    )

    password2 = forms.CharField(
        label=_("Confirm Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": _("Confirm your password"),
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
        return user
