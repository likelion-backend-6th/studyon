from django import forms


class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, label="모집글", required=False)
    tag = forms.CharField(max_length=100, label="태그", required=False)
