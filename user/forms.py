from django import forms
from django.contrib.auth.models import User

from user.models import Profile


class SignupForm(forms.ModelForm):
    username = forms.CharField(label="ID")
    nickname = forms.CharField(label="별명")
    password = forms.CharField(widget=forms.PasswordInput(), label="비밀번호")
    password_check = forms.CharField(widget=forms.PasswordInput(), label="비밀번호 확인")

    class Meta:
        model = User
        fields = ["username", "nickname", "password", "password_check"]

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("아이디가 이미 존재합니다.")
        return username

    def clean_nickname(self):
        nickname = self.cleaned_data["nickname"]
        if Profile.objects.filter(nickname=nickname).exists():
            raise forms.ValidationError("이름이 이미 존재합니다.")
        return nickname

    def clean_password_check(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_check = cleaned_data.get("password_check")

        if password != password_check:
            raise forms.ValidationError("비밀번호와 비밀번호 확인이 같지않습니다.")
        return password_check
