# Generated by Django 4.2.5 on 2023-09-28 11:46

from django.db import migrations
import markdownx.models


class Migration(migrations.Migration):
    dependencies = [
        ("manager", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="content",
            field=markdownx.models.MarkdownxField(),
        ),
    ]
