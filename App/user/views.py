from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView
from django.contrib.auth.views import LoginView as AuthLoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from .forms import RegistrationForm

# Create your views here.
class HomeView(TemplateView):
    template_name = 'user/home.html'
    success_url = reverse_lazy('user:login')

class RegisterView(FormView):
    template_name = 'user/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('user:login')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super().form_valid(form)
class LoginView(AuthLoginView):
    template_name = 'user/login.html'
    # redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('rawina:dashboard')

class LogoutView(LogoutView):
    next_page = reverse_lazy('user:home')
    
class AccountSettingsView(TemplateView):
    template_name = 'user/account.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class EditProfileView(TemplateView):
    template_name = 'user/edit_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()
        return redirect('user:account_settings')

class ChangePasswordView(TemplateView):
    template_name = 'user/change_password.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

    def post(self, request, *args, **kwargs):
        user = request.user
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect('user:change_password')

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect('user:change_password')

        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters.")
            return redirect('user:change_password')

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur

        messages.success(request, "Your password has been changed successfully.")
        return redirect('user:account_settings')
    