from django import forms
from rawina.models import Story


class StoryGenerationForm(forms.Form):
    name = forms.CharField(label="Your Name", max_length=100)
    character = forms.CharField(label="Main Character", max_length=100)
    place = forms.CharField(label="Story Place", max_length=100)
    theme = forms.CharField(widget=forms.HiddenInput())


class ChooseThemeForm(forms.Form):
    theme = forms.ChoiceField(
        choices=[
            ("fantasy", "Fantasy"),
            ("animals", "Animals"),
            ("daily_hero", "Daily Hero"),
        ],
        widget=forms.RadioSelect,
    )


from django import forms


class NarratorSetupForm(forms.Form):
    character_name = forms.CharField(label="Character Name", max_length=30)
    character_type = forms.CharField(
        label="Character Type",
        max_length=100,
        help_text="e.g., a brave child, a clever fox...",
    )
    setting = forms.CharField(
        label="Setting",
        max_length=100,
        help_text="e.g., an enchanted forest, a flying train...",
    )
    theme = forms.CharField(
        label="Theme",
        max_length=100,
        help_text="e.g., adventure, friendship, courage...",
    )
