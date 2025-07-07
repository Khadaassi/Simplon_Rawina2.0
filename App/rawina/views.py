import os
import requests
import threading
from pathlib import Path
from dotenv import load_dotenv
from xhtml2pdf import pisa

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView

from .forms import StoryGenerationForm, ChooseThemeForm
from .models import Story

load_dotenv()
API_URL = os.getenv("RAWINA_API_URL")


def _generate_and_save(story_id, payload):
    """
    Background task: call the API and update story fields (text).
    """
    try:
        resp = requests.post(API_URL, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()
        print("API response:", data)
        text = data.get("story", "")
    except Exception:
        text = "⚠️ Failed to generate story."

    story = Story.objects.get(pk=story_id)
    story.generated_text = text

    story.save()


class DashboardView(TemplateView):
    template_name = "rawina/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx["stories"] = Story.objects.filter(user=self.request.user).order_by("-created_at")[:3]
        return ctx


class DashboardView(TemplateView):
    template_name = "rawina/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx["stories"] = Story.objects.filter(user=self.request.user).order_by("-created_at")[:3]
        return ctx


class StoryListView(ListView):
    model = Story
    template_name = "rawina/story_list.html"
    context_object_name = "stories"

    def get_queryset(self):
        print("MEDIA_ROOT:", settings.MEDIA_ROOT)
        return Story.objects.filter(user=self.request.user).order_by("-created_at")

    def get(self, request, *args, **kwargs):
        if request.GET.get("pdf") and request.GET.get("id"):
            story = get_object_or_404(Story, id=request.GET["id"], user=request.user)
            html = render_to_string("rawina/story_pdf.html", {"story": story})
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename="{story.title}.pdf"'
            pisa.CreatePDF(html, dest=response)
            return response
        
        return super().get(request, *args, **kwargs)


class StoryDetailView(DetailView):
    model = Story
    template_name = "rawina/story_detail.html"
    context_object_name = "story"

    def get_queryset(self):
        return Story.objects.filter(user=self.request.user)


class ChooseThemeView(FormView):
    template_name = "rawina/choose_theme.html"
    form_class = ChooseThemeForm

    def form_valid(self, form):
        selected = form.cleaned_data["theme"]
        return redirect(f"{reverse('rawina:create')}?theme={selected}")


class StoryCreateView(FormView):
    template_name = "rawina/create_story.html"
    form_class = StoryGenerationForm

    def get_initial(self):
        initial = super().get_initial()
        theme = self.request.GET.get("theme")
        if theme:
            initial["theme"] = theme
        return initial

    def form_valid(self, form):
        payload = {
            "user_id": str(self.request.user.id),
            "theme": form.cleaned_data["theme"],
            "name": form.cleaned_data["name"],
            "creature": form.cleaned_data["character"],
            "place": form.cleaned_data["place"],
        }

        story = Story.objects.create(
            user=self.request.user,
            title=f"{form.cleaned_data['name'].capitalize()}'s Story",
            theme=payload["theme"],
            prompt="",
            generated_text="",
        )

        threading.Thread(
            target=_generate_and_save,
            args=(story.pk, payload),
            daemon=True
        ).start()

        return render(self.request, "rawina/loading_story.html", {
            "story_id": story.pk,
        })


class StoryStatusView(View):
    """
    Returns JSON status of story generation for polling.
    """
    def get(self, request, pk):
        story = get_object_or_404(Story, pk=pk, user=request.user)
        return JsonResponse({
            "ready": bool(story.generated_text),
            "url": reverse("rawina:story", kwargs={"pk": story.pk})
        })


class StoryDeleteView(View):
    """
    Deletes a story and redirects to list view.
    """
    def post(self, request, pk):
        story = get_object_or_404(Story, pk=pk, user=request.user)
        story.delete()
        return redirect(reverse("rawina:story_list"))
