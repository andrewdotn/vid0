import os

from django import forms
from django.core.exceptions import ValidationError

VIDEO_FILE_EXTENSIONS = frozenset(
    [
        ".m4a",
        ".m4v",
        ".mkv",
        ".mov",
        ".mp4",
    ]
)


def validate_file_listing(file_listing):
    video_files, errors = extract_files(file_listing)

    if errors:
        raise ValidationError("; ".join(errors))

    if len(video_files) == 0:
        raise ValidationError("No files provided")


def extract_files(file_listing):
    errors = []
    video_files = []

    for row in file_listing.split("\n"):
        row = row.strip()
        if not row:
            continue

        if not any(row.endswith(ext) for ext in VIDEO_FILE_EXTENSIONS):
            errors.append(f"{row!r} does not have a valid video file extension")
            continue

        if not os.path.isfile(row):
            errors.append(f"{row!r} does not exist")
            continue

        video_files.append(row)

    return video_files, errors


class AddVideosForm(forms.Form):
    file_listing = forms.CharField(
        widget=forms.Textarea, validators=[validate_file_listing]
    )

    def extract_files(self):
        return extract_files(self.cleaned_data["file_listing"])
