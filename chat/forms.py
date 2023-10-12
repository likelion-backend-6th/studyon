from django import forms
from django.core.exceptions import ValidationError

from taggit.models import Tag


class TagsForm(forms.Form):
    tag_name = forms.CharField(
        label="",
        required=True,
        widget=forms.TextInput(
            attrs={"class": "my-custom-class", "placeholder": "Enter tags..."}
        ),
    )

    def clean_tag_name(self):
        tag_name = self.cleaned_data.get("tag_name")
        try:
            tag = Tag.objects.get(name=tag_name)
        except Tag.DoesNotExist:
            raise ValidationError("Tag does not exist")
