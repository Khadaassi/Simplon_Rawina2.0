from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Story(models.Model):
    THEME_CHOICES = [
        ("animals", _("Animals")),
        ("fantasy", _("Fantasy")),
        ("daily_hero", _("Daily Hero")),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="stories",
        verbose_name=_("User")
    )
    title = models.CharField(_("Title"), max_length=100)
    theme = models.CharField(_("Theme"), max_length=20, choices=THEME_CHOICES)
    generated_text = models.TextField(_("Generated Text"), help_text=_("Automatically generated text"))

    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.title} – {self.user.username} ({self.created_at.date()})"
