from django.db import models
from django.contrib.auth.models import User


class Story(models.Model):
    THEME_CHOICES = [
        ("animals", "Animals"),
        ("fantasy", "Fantasy"),
        ("daily_hero", "Daily Hero"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="stories")
    title = models.CharField(max_length=100)
    theme = models.CharField(max_length=20, choices=THEME_CHOICES)
    generated_text = models.TextField(help_text="Texte généré automatiquement")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} – {self.user.username} ({self.created_at.date()})"
