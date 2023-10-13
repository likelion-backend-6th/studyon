from django import forms
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory

from markdownx.fields import MarkdownxFormField
from markdownx.widgets import MarkdownxWidget

from .models import File, Post, Study, Task


class StudyForm(forms.ModelForm):
    start = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))

    class Meta:
        model = Study
        fields = ["title", "start", "end", "process", "info"]


class TaskForm(forms.ModelForm):
    start = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "bg-neutral-100 px-2 rounded-md",
                "placeholder": "시작일 선택",
            }
        )
    )
    end = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "bg-neutral-100 px-2 rounded-md",
                "placeholder": "종료일 선택",
            }
        )
    )

    class Meta:
        model = Task
        fields = ["title", "description", "start", "end"]


class FileUploadForm(forms.ModelForm):
    file = forms.FileField(
        label="",
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "file:border-none file:bg-neutral-200 file:hover:bg-neutral-300 file:rounded-sm cursor-pointer"
            }
        ),
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


FileUploadFormSet = modelformset_factory(File, form=FileUploadForm, extra=1, max_num=5)


class FileForm(forms.ModelForm):
    checkbox = forms.BooleanField(
        label="", required=False, widget=forms.CheckboxInput(), initial=True
    )
    url = forms.URLField(
        label="",
        disabled=True,
        required=False,
        widget=forms.FileInput(
            attrs={
                "class": "file:border-none file:bg-neutral-200 file:hover:bg-neutral-300 file:rounded-sm cursor-pointer"
            }
        ),
    )

    class Meta:
        model = File
        fields = ("url", "checkbox")


class PostActionForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "w-full",
                "placeholder": "제목을 입력해주세요.",
            }
        )
    )
    content = MarkdownxFormField(
        required=False,
        widget=MarkdownxWidget(
            attrs={
                "style": "display: none",
            }
        ),
    )

    class Meta:
        model = Post
        fields = (
            "title",
            "content",
        )
