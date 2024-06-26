from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vid0", "0005_series_alter_episode_options_episode_filename_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="series",
            name="slug",
            field=models.SlugField(default="", max_length=255, unique=True),
            preserve_default=False,
        ),
    ]
