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
            ('fantasy', 'Fantasy'),
            ('animals', 'Animals'),
            ('daily_hero', 'Daily Hero'),
        ],
        widget=forms.RadioSelect
    )

