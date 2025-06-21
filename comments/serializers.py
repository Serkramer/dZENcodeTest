import bleach
from captcha.models import CaptchaStore
from rest_framework import serializers

from dZENcodeTest import settings
from dZENcodeTest.settings import ALLOWED_TAGS, ALLOWED_ATTRIBUTES
from .functions import resize_image_if_needed
from .models import CommentFile, Comment


class CommentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentFile
        fields = ['id', 'file', 'uploaded_at']


class CommentSerializer(serializers.ModelSerializer):
    files = CommentFileSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'user_name', 'email', 'home_page', 'text', 'created_at', 'parent', 'files', 'replies']

    def get_replies(self, obj):
        children = obj.replies.all().order_by('created_at')
        return CommentSerializer(children, many=True, context=self.context).data


class CreateCommentSerializer(serializers.ModelSerializer):
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Comment
        fields = ['user_name', 'email', 'home_page', 'text', 'parent', 'files', 'captcha_key', 'captcha_value']

    def validate_user_name(self, value):
        if not value.isalnum():
            raise serializers.ValidationError("Только латинские буквы и цифры.")
        return value

    def validate_text(self, value):
        value = bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)
        if len(value) > 5000:
            raise serializers.ValidationError("Максимальная длина комментария — 5000 символов.")
        return value

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        comment = Comment.objects.create(**validated_data)

        for file in files:
            processed_file = resize_image_if_needed(file)
            CommentFile.objects.create(comment=comment, file=processed_file)

        return comment

    def validate(self, attrs):
        key = attrs.pop('captcha_key', None)
        value = attrs.pop('captcha_value', '').strip().lower()

        try:
            captcha = CaptchaStore.objects.get(hashkey=key)
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError({'captcha': 'Недействительный ключ CAPTCHA.'})

        if captcha.response != value:
            raise serializers.ValidationError({'captcha': 'Неверная CAPTCHA.'})

        captcha.delete()  # знищуємо після використання
        return super().validate(attrs)


    def validate_files(self, files):
        allowed_extensions = getattr(settings, 'ALLOWED_EXTENSIONS', ['jpg', 'jpeg', 'png', 'gif', 'txt'])
        for file in files:
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise serializers.ValidationError(f"{file.name}: запрещённый формат.")
            if ext == 'txt' and file.size > 100 * 1024:
                raise serializers.ValidationError(f"{file.name}: TXT-файл > 100КБ.")
        return files
