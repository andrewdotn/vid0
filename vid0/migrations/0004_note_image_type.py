from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vid0", "0003_alter_episode_options_note_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="note",
            name="image_type",
            field=models.CharField(default="image/jpeg", max_length=255),
            preserve_default=False,
        ),
    ]
