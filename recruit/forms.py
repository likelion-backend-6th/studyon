from django import forms
from django.core.exceptions import ValidationError

from recruit.models import Register, Recruit


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, label="모집글", required=False)
    tag = forms.CharField(max_length=100, label="태그", required=False)


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Register
        fields = ["content"]


class RecruitForm(forms.ModelForm):
    start = forms.DateField(label="시작일", widget=forms.DateInput(attrs={"type": "date"}))
    end = forms.DateField(label="종료일", widget=forms.DateInput(attrs={"type": "date"}))
    deadline = forms.DateField(label="마감일", widget=forms.DateInput(attrs={"type": "date"}))
    total_seats = forms.IntegerField(initial=2, min_value=2, label="모집 인원")
    file = forms.FileField(required=False, label="파일")

    class Meta:
        model = Recruit
        fields = [
            "title",
            "tags",
            "deadline",
            "start",
            "end",
            "total_seats",
            "target",
            "process",
            "info",
            "file",
        ]

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if file.size > 3 * 1024 * 1024:  # 3MB
                raise ValidationError("Maximum File Size: 3MB")
        return file
