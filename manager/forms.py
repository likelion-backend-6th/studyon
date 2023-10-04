from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory

from markdownx.fields import MarkdownxFormField

from .models import File, Post, Study, Task


class StudyForm(forms.ModelForm):
    start = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Study
        fields = ["title", "tags", "start", "end", "process", "info"]


class TaskForm(forms.ModelForm):
    start = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Task
        fields = ["title", "description", "start", "end"]


class FileForm(forms.ModelForm):
    file = forms.FileField(
        label="",
        required=False,
        widget=forms.FileInput(attrs={"class": "file"}),
    )

    class Meta:
        model = File
        fields = ("file",)

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if file.size > 3 * 1024 * 1024:  # 3MB
                raise ValidationError("Maximum File Size: 3MB")
        return file


FileFormSet = modelformset_factory(File, form=FileForm, extra=1, max_num=5)


class FileUpdateForm(forms.ModelForm):
    file = forms.FileField(
        label="",
        required=False,
        widget=forms.FileInput(attrs={"class": "file"}),
    )
    checkbox = forms.BooleanField(
        label="", required=False, widget=forms.CheckboxInput()
    )
    url = forms.URLField(label="", disabled=True, required=False)

    class Meta:
        model = File
        fields = ("file", "url", "checkbox")

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if file.size > 3 * 1024 * 1024:  # 3MB
                raise ValidationError("Maximum File Size: 3MB")
        return file


class PostActionForm(forms.ModelForm):
    content = MarkdownxFormField()

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
        )
