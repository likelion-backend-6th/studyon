from django import forms

from .models import Study


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ["title", "tags", "start", "end", "process", "info"]
