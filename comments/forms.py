from django import forms

from captcha.fields import CaptchaField
from django.core.validators import MaxLengthValidator

from dZENcodeTest.settings import ALLOWED_TAGS, ALLOWED_ATTRIBUTES

import bleach
import re



class CommentForm(forms.Form):
    user_name = forms.CharField(
        max_length=255,
        label="User Name *",
        help_text="Только латинские буквы и цифры.",
        widget=forms.TextInput(attrs={
            'placeholder': 'User123',
            'class': 'form-control',
            'pattern': '[a-zA-Z0-9]+',
            'title': 'Допустимы только латинские буквы и цифры.'
        }),
    )

    email = forms.EmailField(
        label="Email *",
        help_text="Введите корректный email.",
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@example.com',
            'class': 'form-control',
            'title': 'Введите корректный email.',
            'required': True
        }),
    )

    home_page = forms.URLField(
        label="Ссылка на сайт (необязательно)",
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'https://', 'class': 'form-control'}),
    )

    text = forms.CharField(
        label="Text*",
        validators=[MaxLengthValidator(3000)],
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Введите текст сообщения...', 'class': 'form-control'}),
    )

    captcha = CaptchaField(label='Введите CAPTCHA')

    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    def clean_user_name(self):
        username = self.cleaned_data['user_name']
        if not re.fullmatch(r'[a-zA-Z0-9]+', username):
            raise forms.ValidationError("Можно вводить только латинские буквы и цифры.")
        return username

    def clean_text(self):
        raw_text = self.cleaned_data['text']
        cleaned = bleach.clean(raw_text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
        return cleaned

    def clean_home_page(self):
        home_page = self.cleaned_data.get('home_page', '')
        if home_page and not re.match(r'^https?://', home_page):
            home_page = 'https://' + home_page
        return home_page

