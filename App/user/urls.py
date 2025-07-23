from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

from .views import (
    HomeView,
    RegisterView,
    LoginView,
    # LogoutView,
    AccountSettingsView,
    EditProfileView,
    ChangePasswordView,
)

app_name = "user"

urlpatterns = [
    path("home/", HomeView.as_view(), name="home"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("account/", AccountSettingsView.as_view(), name="account_settings"),
    path("edit_profile/", EditProfileView.as_view(), name="edit_profile"),
    path("change_password/", ChangePasswordView.as_view(), name="change_password"),
    path("logout/", LogoutView.as_view(next_page=reverse_lazy("user:home")), name="logout"),
    path("password_reset/", auth_views.PasswordResetView.as_view(
        template_name="user/password_reset.html",
        email_template_name="user/password_reset_email.html",
        subject_template_name="user/password_reset_subject.txt"
    ), name="password_reset"),
    ]
