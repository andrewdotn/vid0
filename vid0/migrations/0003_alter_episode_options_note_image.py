from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vid0", "0002_alter_episode_name"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="episode",
            options={"ordering": ("name",)},
        ),
        migrations.AddField(
            model_name="note",
            name="image",
            field=models.BinaryField(default=b""),
            preserve_default=False,
        ),
    ]
