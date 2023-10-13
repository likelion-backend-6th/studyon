# Generated by Django 4.2.5 on 2023-10-13 12:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="room",
            name="tags",
        ),
        migrations.AddField(
            model_name="room",
            name="category",
            field=models.IntegerField(
                choices=[(1, "계획"), (2, "진행"), (3, "질의응답"), (4, "리뷰"), (5, "기타")],
                default=1,
            ),
            preserve_default=False,
        ),
    ]