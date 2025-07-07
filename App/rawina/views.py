import threading
from pathlib import Path
from xhtml2pdf import pisa

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView

from .forms import StoryGenerationForm, ChooseThemeForm
from .models import Story

from ia_engine.nodes.scenarist import improve_prompt
from ia_engine.llm_loader import get_llm
from ia_engine.nodes.reviewer import review_story


def _generate_and_save(story_id, payload):
    """
    Génère l’histoire localement avec Mistral (via LangChain) et sauvegarde le résultat.
    """
    enriched_prompt = payload.get("enriched_prompt", "")
    llm = get_llm()

    try:
        # génération brute
        raw_text = llm.invoke(
            f"Here is a detailed prompt for a children's story:\n\n{enriched_prompt}\n\n"
            "Write a coherent, magical story in English for a child aged 6 to 10. "
            "Keep it between 10 and 15 sentences, with a warm and vivid tone."
        ).content
        story_text = review_story(raw_text)
    except Exception as e:
        print("Erreur génération :", e)
        story_text = "⚠️ Erreur lors de la génération de l’histoire."

    story = Story.objects.get(pk=story_id)
    story.generated_text = story_text
    story.save()


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
        # Données brutes utilisateur
        user_input = {
            "nom": form.cleaned_data["name"],
            "créature": form.cleaned_data["character"],
            "lieu": form.cleaned_data["place"],
            "thème": form.cleaned_data["theme"]
        }

        # Prompt enrichi (non stocké, non affiché)
        enriched_prompt = improve_prompt(user_input)

        # Payload local uniquement
        payload = {
            "user_id": str(self.request.user.id),
            "theme": form.cleaned_data["theme"],
            "enriched_prompt": enriched_prompt
        }

        story = Story.objects.create(
            user=self.request.user,
            title=f"{form.cleaned_data['name'].capitalize()}'s Story",
            theme=form.cleaned_data["theme"],
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
    def get(self, request, pk):
        story = get_object_or_404(Story, pk=pk, user=request.user)
        return JsonResponse({
            "ready": bool(story.generated_text),
            "url": reverse("rawina:story", kwargs={"pk": story.pk})
        })


class StoryDeleteView(View):
    def post(self, request, pk):
        story = get_object_or_404(Story, pk=pk, user=request.user)
        story.delete()
        return redirect(reverse("rawina:story_list"))
