from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vid0", "0006_series_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="slug",
            field=models.SlugField(default="", max_length=255),
            preserve_default=False,
        ),
    ]
