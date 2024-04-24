from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("vid0", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="episode",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
