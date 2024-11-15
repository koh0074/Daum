from django import forms
from .models import Post, Tag

class PostForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label="태그"
    )
    image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),
        label="이미지 업로드"
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'location', 'rating', 'tags', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '위치를 입력하세요'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 3}),
        }

    def clean_tags(self):
        tags = self.cleaned_data.get('tags', None)
        if tags is None:
            return []  # 태그가 없을 경우 빈 리스트를 반환
        return tags
