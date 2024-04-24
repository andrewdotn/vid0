import pytest


@pytest.fixture(autouse=True, scope="session")
def temporary_media_root(tmp_path_factory):
    """If any file fields like images are saved during tests, we don’t want them
    cluttering up the dev media folder, so use a temporary one.
    """

    from django.conf import settings

    settings.MEDIA_ROOT = tmp_path_factory.mktemp("media")
