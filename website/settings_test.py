import pytest

from website.util import insert_app_after_django_apps


@pytest.mark.parametrize(
    ("installed_apps", "new_app", "expected"),
    [
        ([], "foo", ["foo"]),
        (
            ["django.this", "django.that"],
            "foo",
            ["django.this", "django.that", "foo"],
        ),
        (
            ["django.this", "django.that", "something.else"],
            "foo",
            ["django.this", "django.that", "foo", "something.else"],
        ),
    ],
)
def test_insert_after_django_apps(installed_apps, new_app, expected):
    assert expected == insert_app_after_django_apps(installed_apps, new_app)
