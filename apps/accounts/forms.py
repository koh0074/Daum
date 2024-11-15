from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class SignupForm(UserCreationForm):
    nickname = forms.CharField(
        label='닉네임',
        widget=forms.TextInput(attrs={'class': 'signup-input'})
    )
    username = forms.CharField(
        label='아이디',
        widget=forms.TextInput(attrs={'class': 'signup-input'})
    )
    password1 = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={'class': 'signup-input'})
    )

    class Meta:
        model = User
        fields = ['nickname', 'username', 'password1']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")

        # 비밀번호 검증 로직 추가 (password2를 사용하지 않음)
        if not password1:
            raise forms.ValidationError("비밀번호를 입력해주세요.")
        return cleaned_data
