import json
from pathlib import Path

from django.core.management.utils import get_random_secret_key


def load_or_generate_secret_key(base_dir):
    """Load or generate a secret key, stored in BASE_DIR / .secrets.json

    Instead of checking in an insecure key, use a local file to store it,
    automatically generating it if needed.
    """
    secrets_file: Path = base_dir / ".secrets.json"
    if not secrets_file.exists():
        secrets = {}
    else:
        secrets = json.loads(secrets_file.read_text())

    # XXX There’s a potential race condition here if multiple django processes
    # all start up at once for the first time.
    secret_key = secrets.get("SECRET_KEY", None)
    if secret_key is None:
        secret_key = get_random_secret_key()

        secrets["SECRET_KEY"] = secret_key
        secrets_file.write_text(json.dumps(secrets, indent=True) + "\n")

    return secret_key


def insert_app_after_django_apps(installed_apps, new_app):
    """Add the given entry to the list, after all the initial django.* things.

    This is what the django-debug-toolbar docs say to do.
    """
    for i, existing_app in enumerate(installed_apps):
        if not existing_app.startswith("django."):
            return installed_apps[:i] + [new_app] + installed_apps[i:]
    return installed_apps + [new_app]
