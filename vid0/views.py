import base64
import datetime
import json
import os
from pathlib import Path

from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.text import slugify
from django.views.generic import ListView, CreateView

from vid0.forms import AddVideosForm
from vid0.models import Episode, Note, Series
from vid0.webvtt import whisper_json_to_webvtt


class SeriesCreateView(CreateView):
    model = Series
    fields = ("name",)

    def form_valid(self, form):
        form.instance.slug = slugify(form.instance.name)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("vid0:home")


def add_episodes(request):
    series = get_object_or_404(Series, slug=request.GET.get("series"))

    if request.POST:
        form = AddVideosForm(request.POST)

        if form.is_valid():
            video_files, errors = form.extract_files()
            assert not errors

            for v in video_files:
                filename = os.path.basename(v)
                root, ext = os.path.splitext(filename)

                Episode.objects.create(
                    series=series, filename=v, name=root, slug=slugify(root)
                )

            return redirect("vid0:home")

    else:
        form = AddVideosForm()

    return render(request, "vid0/add_episodes.html", {"form": form, "series": series})


class VideoListView(ListView):
    model = Series
    template_name = "vid0/video_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related("episode_set", "episode_set__note_set")
        return qs


def view_video(request, series_slug, episode_slug):
    series = get_object_or_404(Series, slug=series_slug)
    episode = get_object_or_404(Episode, series=series, slug=episode_slug)
    return render(
        request, "vid0/video.html", context={"series": series, "episode": episode}
    )


def serve_video_file(request, series_slug, episode_slug):
    series = get_object_or_404(Series, slug=series_slug)
    episode = get_object_or_404(Episode, series=series, slug=episode_slug)

    file = Path(episode.filename).read_bytes()
    return HttpResponse(file, content_type="video/mp4")


def serve_webvtt(request, series_slug, episode_slug):
    series = get_object_or_404(Series, slug=series_slug)
    episode = get_object_or_404(Episode, series=series, slug=episode_slug)

    vtt_file = episode.path.with_suffix(".vtt")
    if vtt_file.exists():
        return HttpResponse(vtt_file.read_bytes(), content_type="text/vtt")

    whisper_json_file = episode.path.with_suffix(".whisper.json")
    if whisper_json_file.exists():
        webvtt = whisper_json_to_webvtt(json.loads(whisper_json_file.read_text()))
        return HttpResponse(webvtt, content_type="text/vtt")

    raise Http404()


class NoteList(ListView):
    model = Note
    ordering = "timestamp"


def save_note(request):
    payload = json.loads(request.body)

    episode = Episode.objects.get(
        series__slug=payload["seriesSlug"], slug=payload["episodeSlug"]
    )
    note = Note.objects.create(
        episode=episode,
        video_position=payload["videoPosition"],
        timestamp=datetime.datetime.now().astimezone(),
        text=payload["text"],
        image=base64.b64decode(payload["image"]),
        # TODO: validate image type
        image_type=payload["imageType"],
    )

    print(note)
    return JsonResponse({"ok": True, "noteId": note.id})
