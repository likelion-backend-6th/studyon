from django import forms

from recruit.models import Register, Recruit


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, label="모집글", required=False)
    tag = forms.CharField(max_length=100, label="태그", required=False)


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Register
        fields = ["content"]


class RecruitForm(forms.ModelForm):
    start = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    deadline = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    total_seats = forms.IntegerField(initial=2)

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
            "files",
        ]
