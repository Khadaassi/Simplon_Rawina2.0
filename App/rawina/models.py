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
    title_fr = models.CharField(_("Title"), max_length=100, null=True, blank=True)
    title_en = models.CharField(_("Title (English)"), max_length=100, null=True, blank=True)
    theme = models.CharField(_("Theme"), max_length=20, choices=THEME_CHOICES)
    generated_text_en = models.TextField(_("Generated Text (English)"), help_text=_("Automatically generated text"), null=True, blank=True)
    generated_text_fr = models.TextField(_("Generated Text (French)"), help_text=_("Automatically generated text"), null=True, blank=True)
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True)

    def __str__(self):
        return f"{self.title} – {self.user.username} ({self.created_at.date()})"
