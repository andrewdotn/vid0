import base64
from pathlib import Path

from django.db import models
from django.utils.text import slugify

DEFAULT_MAX_LENGTH = 255


class Series(models.Model):
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    slug = models.SlugField(max_length=DEFAULT_MAX_LENGTH, unique=True)


class Episode(models.Model):
    series = models.ForeignKey(to=Series, on_delete=models.RESTRICT)
    name = models.CharField(max_length=DEFAULT_MAX_LENGTH, unique=True)
    filename = models.TextField()
    slug = models.SlugField(max_length=DEFAULT_MAX_LENGTH)

    @property
    def path(self):
        return Path(self.filename)

    class Meta:
        ordering = (
            "series",
            "name",
        )


class Note(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.RESTRICT)
    video_position = models.CharField(max_length=DEFAULT_MAX_LENGTH)
    timestamp = models.DateTimeField()  # when note created
    text = models.TextField()
    image = models.BinaryField()
    image_type = models.CharField(max_length=DEFAULT_MAX_LENGTH)

    def image_data_url(self):
        return (
            "data:"
            + self.image_type
            + ";base64,"
            + base64.b64encode(self.image).decode("US-ASCII")
        )
