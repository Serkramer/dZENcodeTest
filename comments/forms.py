from django import forms
from django.core.validators import FileExtensionValidator
from django.forms import modelformset_factory, ClearableFileInput
from captcha.fields import CaptchaField
from .models import Comment, CommentFile
import bleach

ALLOWED_TAGS = ['a', 'code', 'i', 'strong']
ALLOWED_ATTRIBUTES = {'a': ['href', 'title']}
#
#
# class MultiFileInput(ClearableFileInput):
#     allow_multiple_selected = True
#
#
# class CommentForm(forms.ModelForm):
#     captcha = CaptchaField(label='Введите CAPTCHA')
#
#     class Meta:
#         model = Comment
#         fields = ['user_name', 'email', 'home_page', 'text', 'captcha', 'parent']
#
#     def clean_user_name(self):
#         username = self.cleaned_data['user_name']
#         if not username.isalnum():
#             raise forms.ValidationError("Можно вводить только латинские буквы и цифры.")
#         return username
#
#     def clean_text(self):
#         raw_text = self.cleaned_data['text']
#         cleaned = bleach.clean(raw_text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
#         return cleaned
#
#     def save(self, commit=True):
#         comment = super().save(commit=False)
#         parent_id = self.cleaned_data.get('parent_id')
#         if parent_id:
#             comment.parent = Comment.objects.filter(id=parent_id).first()
#         if commit:
#             comment.save()
#         return comment
#
#
#
# class CommentFileForm(forms.ModelForm):
#     class Meta:
#         model = CommentFile
#         fields = ['file']
#         widgets = {
#             'file': MultiFileInput(attrs={'multiple': True})
#         }
#
#     def clean_file(self):
#         file = self.cleaned_data['file']
#         ext = file.name.split('.')[-1].lower()
#         if ext not in ['jpg', 'jpeg', 'png', 'gif', 'txt']:
#             raise forms.ValidationError(f"{file.name}: допустимы только JPG, JPEG, PNG, GIF, TXT.")
#         if ext == 'txt' and file.size > 100 * 1024:
#             raise forms.ValidationError(f"{file.name}: TXT-файл не должен превышать 100 КБ.")
#         return file
#
#
# CommentFileFormSet = modelformset_factory(
#     CommentFile,
#     form=CommentFileForm,
#     extra=0,
#     can_delete=False
# )

class MultipleFileInput(ClearableFileInput):
    allow_multiple_selected = True


class CommentForm(forms.Form):
    user_name = forms.CharField(
        max_length=255,
        label="User Name",
        help_text="Только латинские буквы и цифры.",
        widget=forms.TextInput(attrs={'placeholder': 'User123', 'class': 'form-control'}),
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'placeholder': 'example@example.com', 'class': 'form-control'}),
    )

    home_page = forms.URLField(
        label="Home page",
        required=False,
        widget=forms.URLInput(attrs={'placeholder': 'https://', 'class': 'form-control'}),
    )

    text = forms.CharField(
        label="Text",
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Введите текст сообщения...', 'class': 'form-control'}),
    )

    captcha = CaptchaField(label='Введите CAPTCHA')

    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)


    def clean_user_name(self):
        username = self.cleaned_data['user_name']
        if not username.isalnum():
            raise forms.ValidationError("Можно вводить только латинские буквы и цифры.")
        return username

    def clean_text(self):
        raw_text = self.cleaned_data['text']
        cleaned = bleach.clean(raw_text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
        return cleaned

    def clean_home_page(self):
        home_page = self.cleaned_data.get('home_page')
        if home_page == '':
            return None
        return home_page

