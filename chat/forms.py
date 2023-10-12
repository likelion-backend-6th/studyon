from django import forms


class TagsForm(forms.Form):
    tags = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "my-custom-class", "placeholder": "Enter tags..."}
        )
    )
