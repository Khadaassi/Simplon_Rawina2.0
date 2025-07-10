import threading
import base64
import pickle

from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.text import slugify

from xhtml2pdf import pisa

from .forms import StoryGenerationForm, ChooseThemeForm, NarratorSetupForm
from .models import Story

from ia_engine.llm_loader import get_llm
from ia_engine.nodes.scenarist import improve_prompt
from ia_engine.nodes.reviewer import review_story
from ia_engine.nodes.narrator import InteractiveNarrator

# from ia_engine.nodes.cleaner import review_scene_and_choices


# === Static story generation ===
def _generate_and_save(story_id, payload):
    enriched_prompt = payload.get("enriched_prompt", "")
    llm = get_llm()

    try:
        raw_text = llm.invoke(
            f"Here is a detailed prompt for a children's story:\n\n{enriched_prompt}\n\n"
            "Write a coherent, magical story in English for a child aged 6 to 10. "
            "Keep it between 10 and 15 sentences, with a warm and vivid tone."
        ).content
        story_text = review_story(raw_text)
    except Exception as e:
        print("Generation error:", e)
        story_text = "⚠️ Story generation failed."

    story = Story.objects.get(pk=story_id)
    story.generated_text = story_text
    story.save()


# === Dashboard & story views ===
class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "rawina/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ctx["stories"] = Story.objects.filter(user=self.request.user).order_by(
                "-created_at"
            )[:3]
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
            html = render_to_string("rawina/story_pdf.html", {"story": story})
            response = HttpResponse(content_type="application/pdf")
            response["Content-Disposition"] = (
                f'attachment; filename="{story.title}.pdf"'
            )
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

        enriched_prompt = improve_prompt(user_input)

        payload = {
            "user_id": str(self.request.user.id),
            "theme": form.cleaned_data["theme"],
            "enriched_prompt": enriched_prompt,
        }

        story = Story.objects.create(
            user=self.request.user,
            title=f"{form.cleaned_data['name'].capitalize()}'s Story",
            theme=form.cleaned_data["theme"],
            generated_text="",
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
                "ready": bool(story.generated_text),
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
        narrator = InteractiveNarrator()
        narrator.start_story(config)

        raw_bytes = pickle.dumps(narrator)
        encoded = base64.b64encode(raw_bytes).decode("utf-8")
        self.request.session["narrator"] = encoded

        return redirect("rawina:narration")


class InteractiveNarratorView(LoginRequiredMixin, View):
    template_name = "rawina/interactive_narrator.html"

    def get(self, request):
        if request.GET.get("restart") == "1":
            if "narrator" in request.session:
                del request.session["narrator"]
            return redirect("rawina:narration_setup")

        encoded = request.session.get("narrator")
        if not encoded:
            return redirect("rawina:narration_setup")

        raw_bytes = base64.b64decode(encoded)
        narrator = pickle.loads(raw_bytes)

        # Last scene and choices
        last = (
            narrator.history[-1] if narrator.history else {"scene": "", "choices": []}
        )

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
            raise Http404("Narrator session not found.")

        raw_bytes = base64.b64decode(encoded)
        narrator = pickle.loads(raw_bytes)

        user_choice = request.POST.get("choice")
        next_step = narrator.next_scene(user_choice)

        # Save
        request.session["narrator"] = base64.b64encode(pickle.dumps(narrator)).decode(
            "utf-8"
        )
        if narrator.is_finished():
            final_story = narrator.final_story()
            theme = request.session.get("interactive_theme", "Unknown")
            title = slugify(narrator.history[0]['scene'][:30]) or "Interactive Story"

            Story.objects.create(
                user=request.user,
                title=title.capitalize(),
                theme=theme,
                generated_text=final_story
            )
            
        return render(request, self.template_name, {
            "scene": next_step["scene"],
            "choices": next_step["choices"],
            "finished": narrator.is_finished(),
            "history": narrator.history if narrator.is_finished() else None,
        })

    def save_narrator(self, narrator):
        """
        Save the narrator state to the session.
        """
        raw_bytes = pickle.dumps(narrator)
        encoded = base64.b64encode(raw_bytes).decode("utf-8")
        self.request.session["narrator"] = encoded


class InteractiveChooseThemeView(LoginRequiredMixin, FormView):
    template_name = "rawina/interactive_choose_theme.html"
    form_class = ChooseThemeForm

    def form_valid(self, form):
        selected = form.cleaned_data["theme"]
        return redirect(f"{reverse('rawina:narration_setup')}?theme={selected}")
