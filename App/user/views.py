from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from django.utils.translation import gettext as _
from .forms import RegistrationForm
from django.contrib.auth.forms import PasswordChangeForm


class HomeView(TemplateView):
    template_name = "user/home.html"
    success_url = reverse_lazy("user:login")


class RegisterView(FormView):
    template_name = "user/register.html"
    form_class = RegistrationForm
    success_url = reverse_lazy("user:login")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)


class LoginView(AuthLoginView):
    template_name = "user/login.html"

    def get_success_url(self):
        return reverse_lazy("rawina:dashboard")


class LogoutView(LogoutView):
    next_page = reverse_lazy("user:home")


class AccountSettingsView(TemplateView):
    template_name = "user/account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class EditProfileView(TemplateView):
    template_name = "user/edit_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        user.username = request.POST.get("username")
        user.email = request.POST.get("email")
        user.save()
        return redirect("user:account_settings")


class ChangePasswordView(FormView):
    template_name = "user/change_password.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("user:account_settings")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, _("Your password has been changed successfully."))
        return super().form_valid(form)

    def form_invalid(self, form):
        for field_errors in form.errors.values():
            for error in field_errors:
                messages.error(self.request, error)
        return super().form_invalid(form)