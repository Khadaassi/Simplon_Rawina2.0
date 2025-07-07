from django.urls import path

from .views import (
    DashboardView,
    StoryCreateView,
    StoryListView,
    ChooseThemeView,
    StoryDetailView,
    StoryStatusView,
    StoryDeleteView
)
app_name = "rawina"

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("stories/", StoryListView.as_view(), name="story_list"),
    path("story/<int:pk>/", StoryDetailView.as_view(), name="story"),
    path("choose/theme/", ChooseThemeView.as_view(), name="choose_theme"),
    path("create/", StoryCreateView.as_view(), name="create"),
    path("story/<int:pk>/status/", StoryStatusView.as_view(), name="story_status"),
    path("story/<int:pk>/delete/", StoryDeleteView.as_view(), name="story_delete"),
]