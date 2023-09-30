from django import forms

from django.forms import modelformset_factory

from markdownx.fields import MarkdownxFormField

from .models import File, Post, Study


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ["title", "tags", "start", "end", "process", "info"]


class FileForm(forms.ModelForm):
    file = forms.FileField(
        required=False, widget=forms.FileInput(attrs={"class": "file"})
    )

    class Meta:
        model = File
        fields = ("file",)


FileFormSet = modelformset_factory(File, form=FileForm, extra=1, max_num=5)


class PostCreateForm(forms.ModelForm):
    content = MarkdownxFormField()

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
        )
