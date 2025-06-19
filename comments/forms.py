import bleach
from captcha.fields import CaptchaField
from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, CommentFile

ALLOWED_TAGS = ['a', 'code', 'i', 'strong']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}


class CommentForm(forms.ModelForm):
    captcha = CaptchaField(label='Введите CAPTCHA')
    files = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))


    class Meta:
        model = Comment
        fields = ['user_name', 'email', 'home_page', 'text', 'captcha', 'files']


    def clean_user_name(self):
        username = self.cleaned_data['user_name']
        if not username.isalnum():
            raise forms.ValidationError("Можно вводить только латинские символы и цифры")
        return username

    def clean_text(self):
        raw_text = self.cleaned_data['text']
        return bleach.clean(raw_text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

    def clean_files(self):
        pass


e