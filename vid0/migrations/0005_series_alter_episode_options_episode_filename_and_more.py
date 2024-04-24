import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vid0", "0004_note_image_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Series",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name="episode",
            options={"ordering": ("series", "name")},
        ),
        migrations.AddField(
            model_name="episode",
            name="filename",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="episode",
            name="series",
            field=models.ForeignKey(
                default="",
                on_delete=django.db.models.deletion.RESTRICT,
                to="vid0.series",
            ),
            preserve_default=False,
        ),
    ]
