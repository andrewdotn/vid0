from django.urls import path

from . import views
from .apps import Vid0Config

app_name = Vid0Config.name

urlpatterns = [
    path("", views.VideoListView.as_view(), name="home"),
    #
    path("series/new", views.SeriesCreateView.as_view(), name="series_create"),
    path("episode/add", views.add_episodes, name="episodes_add"),
    #
    path("watch/<str:series_slug>/<str:episode_slug>", views.view_video, name="watch"),
    path(
        "mp4/<str:series_slug>/<str:episode_slug>", views.serve_video_file, name="serve"
    ),
    path(
        "vtt/<str:series_slug>/<str:episode_slug>", views.serve_webvtt, name="serve_vtt"
    ),
    #
    path("savenote", views.save_note, name="savenote"),
    path("notes", views.NoteList.as_view(), name="note_list"),
]
