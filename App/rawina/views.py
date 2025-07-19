import threading
import base64
import pickle

from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _, get_language
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import translation

from xhtml2pdf import pisa

from .forms import StoryGenerationForm, ChooseThemeForm, NarratorSetupForm
from .models import Story

from ia_engine.llm_loader import get_groq_llm as get_llm
from ia_engine.nodes.scenarist import improve_prompt
from ia_engine.nodes.reviewer import review_story
from ia_engine.nodes.narrator import InteractiveNarrator
from ia_engine.nodes.title_agent import generate_title_from_story, generate_title_from_scene
from ia_engine.nodes.translator import translate_story, translate_title


# === Static story generation ===
def _generate_and_save(story_id, payload):
    enriched_prompt = payload.get("enriched_prompt", "")
    lang = payload.get("language", "en")
    llm = get_llm()

    try:
        if lang == "fr":
            prompt = (
                f"Voici un prompt détaillé pour une histoire pour enfants :\n\n{enriched_prompt}\n\n"
                "Écris une histoire cohérente en français pour un enfant de 6 à 10 ans. "
                "Entre 20 et 25 phrases, avec un ton chaleureux et imagé."
            )
            raw_text_fr = llm.invoke(prompt).content
            reviewed_fr = review_story(raw_text_fr, language="fr")
            translated_en = translate_story(reviewed_fr, language="en")
            story_text_fr = reviewed_fr
            story_text_en = translated_en
            title_fr = generate_title_from_story(story_text_fr, language=lang) or _("Histoire sans titre")
            title_en = translate_title(title_fr, language="en") or _("Untitled Story")
        else:
            prompt = (
                f"Here is a detailed prompt for a children's story:\n\n{enriched_prompt}\n\n"
                "Write a coherent story in English for a child aged 6 to 10. "
                "Keep it between 20 and 25 sentences, with a warm and vivid tone."
            )
            raw_text_en = llm.invoke(prompt).content
            reviewed_en = review_story(raw_text_en, language="en")
            translated_fr = translate_story(reviewed_en, language="fr")
            story_text_en = reviewed_en
            story_text_fr = translated_fr
            title_en = generate_title_from_story(story_text_en, language=lang) or _("Untitled Story")
            title_fr = translate_title(title_en, language="fr") or _("Histoire sans titre")

    except Exception as e:
        print("Generation error:", e)
        story_text_en = _("⚠️ Story generation failed.")
        story_text_fr = _("⚠️ La génération de l'histoire a échoué.")
        title_fr = _("Histoire sans titre")
        title_en = _("Untitled Story")

    story = Story.objects.get(pk=story_id)
    story.generated_text_fr = story_text_fr
    story.generated_text_en = story_text_en
    story.title_fr = title_fr
    story.title_en = title_en
    story.save()


# === Dashboard & story views ===
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "rawina/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx["stories"] = Story.objects.filter(user=self.request.user).order_by("-created_at")[:3]
        return ctx


class StoryListView(LoginRequiredMixin, ListView):
    model = Story
    template_name = "rawina/story_list.html"
    context_object_name = "stories"

    def get_queryset(self):
        return Story.objects.filter(user=self.request.user).order_by("-created_at")

    def get(self, request, *args, **kwargs):
        if request.GET.get("pdf") and request.GET.get("id"):
            story = get_object_or_404(Story, id=request.GET["id"], user=request.user)

            lang = get_language()  # récupère la langue active du user

            with translation.override(lang):
                html = render_to_string(
                    "rawina/story_pdf.html",
                    {"story": story, "LANGUAGE_CODE": lang},  # assure la présence dans le template
                    request=request,  # utile pour les balises comme {% trans %}
                )

            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename=\"{story.title_fr}.pdf\"' if lang == "fr" else f'attachment; filename=\"{story.title_en}.pdf\"'
            pisa.CreatePDF(html, dest=response)
            return response

        return super().get(request, *args, **kwargs)


class StoryDetailView(LoginRequiredMixin, DetailView):
    model = Story
    template_name = "rawina/story_detail.html"
    context_object_name = "story"

    def get_queryset(self):
        return Story.objects.filter(user=self.request.user)


class ChooseThemeView(LoginRequiredMixin, FormView):
    template_name = "rawina/choose_theme.html"
    form_class = ChooseThemeForm

    def form_valid(self, form):
        selected = form.cleaned_data["theme"]
        return redirect(f"{reverse('rawina:create')}?theme={selected}")


class StoryCreateView(LoginRequiredMixin, FormView):
    template_name = "rawina/create_story.html"
    form_class = StoryGenerationForm

    def get_initial(self):
        initial = super().get_initial()
        theme = self.request.GET.get("theme")
        if theme:
            initial["theme"] = theme
        return initial

    def form_valid(self, form):
        user_input = {
            "name": form.cleaned_data["name"],
            "creature": form.cleaned_data["character"],
            "place": form.cleaned_data["place"],
            "theme": form.cleaned_data["theme"],
        }
        lang = get_language()
        enriched_prompt = improve_prompt(user_input, language=lang)
        title_en = _("{name}'s Story").format(name=form.cleaned_data['name'].capitalize()),
        title_fr = _("L'histoire de {name}").format(name=form.cleaned_data['name'].capitalize())

        payload = {
            "user_id": str(self.request.user.id),
            "theme": form.cleaned_data["theme"],
            "enriched_prompt": enriched_prompt,
            "language": lang,
        }

        story = Story.objects.create(
            user=self.request.user,
            title_en=title_en,
            title_fr=title_fr,
            theme=form.cleaned_data["theme"],
            generated_text_en="",
            generated_text_fr="",
        )

        threading.Thread(
            target=_generate_and_save, args=(story.pk, payload), daemon=True
        ).start()

        return render(
            self.request,
            "rawina/loading_story.html",
            {
                "story_id": story.pk,
            },
        )


class StoryStatusView(LoginRequiredMixin, View):
    def get(self, request, pk):
        story = get_object_or_404(Story, pk=pk, user=request.user)
        return JsonResponse(
            {
                "ready": bool(story.generated_text_en and story.generated_text_fr),
                "url": reverse("rawina:story", kwargs={"pk": story.pk}),
            }
        )


class StoryDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        story = get_object_or_404(Story, pk=pk, user=request.user)
        story.delete()
        return redirect(reverse("rawina:story_list"))


# === Interactive narrator views ===
class NarratorSetupView(LoginRequiredMixin, FormView):
    template_name = "rawina/interactive_create_story.html"
    form_class = NarratorSetupForm

    def get_initial(self):
        initial = super().get_initial()
        theme = self.request.GET.get("theme")
        if theme:
            initial["theme"] = theme
        return initial

    def form_valid(self, form):
        config = form.cleaned_data
        lang = get_language()
        narrator = InteractiveNarrator(language=lang)
        narrator.start_story(config)
        narrator.config = config

        raw_bytes = pickle.dumps(narrator)
        encoded = base64.b64encode(raw_bytes).decode("utf-8")
        self.request.session["narrator"] = encoded

        return redirect("rawina:narration")


class InteractiveNarratorView(LoginRequiredMixin, View):
    template_name = "rawina/interactive_narrator.html"

    def get(self, request):
        if request.GET.get("restart") == "1":
            request.session.pop("narrator", None)
            return redirect("rawina:narration_setup")

        encoded = request.session.get("narrator")
        if not encoded:
            return redirect("rawina:narration_setup")

        narrator = pickle.loads(base64.b64decode(encoded))
        last = narrator.history[-1] if narrator.history else {"scene": "", "choices": []}

        return render(
            request,
            self.template_name,
            {
                "scene": last["scene"],
                "choices": last["choices"],
                "finished": narrator.is_finished(),
                "history": narrator.history if narrator.is_finished() else None,
            },
        )

    def post(self, request):
        encoded = request.session.get("narrator")
        if not encoded:
            raise Http404(_("Narrator session not found."))

        narrator = pickle.loads(base64.b64decode(encoded))
        user_choice = request.POST.get("choice")
        next_step = narrator.next_scene(user_choice)

        request.session["narrator"] = base64.b64encode(pickle.dumps(narrator)).decode("utf-8")

        if narrator.is_finished():
            full_story = narrator.final_story()
            if narrator.language == "fr":
                story_text_fr = full_story
                story_text_en = translate_story(full_story, language="en")
                title_fr = generate_title_from_story(story_text_fr, language=narrator.language) or _("Histoire sans titre")
                title_en = translate_title(title_fr, language="en") or _("Untitled Story")
            else:
                story_text_en = full_story
                story_text_fr = translate_story(full_story, language="fr")
                title_en = generate_title_from_story(story_text_en, language=narrator.language) or _("Untitled Story")
                title_fr = translate_title(title_en, language="fr") or _("Histoire sans titre")
            config = getattr(narrator, "config", {})
            theme = config.get("theme", "")
            scene = narrator.history[0]["scene"]

            Story.objects.create(
                user=self.request.user,
                title_fr=title_fr,
                title_en=title_en,
                theme=theme,
                generated_text_en=story_text_en,
                generated_text_fr=story_text_fr,
            )

        return render(
            request,
            self.template_name,
            {
                "scene": next_step["scene"],
                "choices": next_step["choices"],
                "finished": narrator.is_finished(),
                "history": narrator.history if narrator.is_finished() else None,
            },
        )


class InteractiveChooseThemeView(LoginRequiredMixin, FormView):
    template_name = "rawina/interactive_choose_theme.html"
    form_class = ChooseThemeForm

    def form_valid(self, form):
        selected = form.cleaned_data["theme"]
        return redirect(f"{reverse('rawina:narration_setup')}?theme={selected}")
