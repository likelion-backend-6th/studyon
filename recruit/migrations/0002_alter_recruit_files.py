# Generated by Django 4.2.5 on 2023-09-30 07:38

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("manager", "0002_alter_post_content"),
        ("recruit", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recruit",
            name="files",
            field=models.ManyToManyField(
                blank=True, related_name="recruits", to="manager.file"
            ),
        ),
    ]
