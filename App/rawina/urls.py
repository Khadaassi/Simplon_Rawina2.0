from django.urls import path

from .views import (
    DashboardView,
    StoryCreateView,
    StoryListView,
    ChooseThemeView,
    StoryDetailView,
    StoryStatusView,
    StoryDeleteView,
    InteractiveNarratorView,
    NarratorSetupView,
    InteractiveChooseThemeView,
)

app_name = "rawina"

urlpatterns = [
    # Static story generation
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("choose/theme/", ChooseThemeView.as_view(), name="choose_theme"),
    path("create/", StoryCreateView.as_view(), name="create"),
    path("stories/", StoryListView.as_view(), name="story_list"),
    path("story/<int:pk>/", StoryDetailView.as_view(), name="story"),
    path("story/<int:pk>/status/", StoryStatusView.as_view(), name="story_status"),
    path("story/<int:pk>/delete/", StoryDeleteView.as_view(), name="story_delete"),
    # Interactive narrator
    path("narration/", InteractiveNarratorView.as_view(), name="narration"),
    path(
        "narration/choose-theme/",
        InteractiveChooseThemeView.as_view(),
        name="interactive_choose_theme",
    ),
    path("narration/setup/", NarratorSetupView.as_view(), name="narration_setup"),
]
