from django import forms
from django.utils.translation import gettext_lazy as _
from rawina.models import Story


class StoryGenerationForm(forms.Form):
    name = forms.CharField(label=_("Your Name"), max_length=100)
    character = forms.CharField(label=_("Main Character"), max_length=100)
    place = forms.CharField(label=_("Story Place"), max_length=100)
    theme = forms.CharField(widget=forms.HiddenInput())


class ChooseThemeForm(forms.Form):
    theme = forms.ChoiceField(
        choices=[
            ("fantasy", _("Fantasy")),
            ("animals", _("Animals")),
            ("daily_hero", _("Daily Hero")),
        ],
        widget=forms.RadioSelect,
    )


class NarratorSetupForm(forms.Form):
    character_name = forms.CharField(label=_("Character Name"), max_length=30)
    character_type = forms.CharField(
        label=_("Character Type"),
        max_length=100,
        help_text=_("e.g., a brave child, a clever fox..."),
    )
    setting = forms.CharField(
        label=_("Setting"),
        max_length=100,
        help_text=_("e.g., an enchanted forest, a flying train..."),
    )
    theme = forms.CharField(
        label=_("Theme"),
        max_length=100,
        help_text=_("e.g., adventure, friendship, courage..."),
    )
