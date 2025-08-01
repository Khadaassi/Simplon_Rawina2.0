"""
URL configuration for App project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from django.urls import include, reverse_lazy
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("test/", lambda request: HttpResponse("✅ OK Rawina")),
    path('admin/', admin.site.urls),
    path('', include('user.urls', namespace='user')),
    path('rawina/', include('rawina.urls', namespace='rawina')),
    path('', RedirectView.as_view(url=reverse_lazy('user:home'))),
    path("__reload__/", include("django_browser_reload.urls")),
    path('i18n/', include('django.conf.urls.i18n')),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(
        template_name="user/password_reset_confirm.html"
    ), name="password_reset_confirm"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="user/password_reset_done.html"), name="password_reset_done"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="user/password_reset_complete.html"), name="password_reset_complete"),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
