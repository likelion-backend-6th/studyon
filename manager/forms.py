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
        label="", required=False, widget=forms.FileInput(attrs={"class": "file"})
    )

    class Meta:
        model = File
        fields = ("file",)


FileFormSet = modelformset_factory(File, form=FileForm, extra=1, max_num=5)


class FileUpdateForm(forms.ModelForm):
    file = forms.FileField(
        label="", required=False, widget=forms.FileInput(attrs={"class": "file"})
    )
    checkbox = forms.BooleanField(
        label="", required=False, widget=forms.CheckboxInput()
    )
    url = forms.URLField(label="", disabled=True, required=False)

    class Meta:
        model = File
        fields = ("file", "url", "checkbox")


class PostActionForm(forms.ModelForm):
    content = MarkdownxFormField()

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
        )
