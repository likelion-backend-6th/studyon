from django import forms

from chat.models import Room


class CategoryForm(forms.Form):
    category = forms.ChoiceField(
        label="",
        required=True,
        widget=forms.Select(
            attrs={"class": "text-center mx-2 my-custom-class"},
        ),
        choices=[(0, "카테고리 선택")] + Room.CategoryChoices.choices,
    )

    def clean_category(self):
        category = int(self.cleaned_data.get("category"))
        if not category:
            raise forms.ValidationError("Category does not exist")

        return category
