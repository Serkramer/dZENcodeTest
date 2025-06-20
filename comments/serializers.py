import bleach
from rest_framework import serializers

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
    files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Comment
        fields = ['user_name', 'email', 'home_page', 'text', 'parent', 'files']

    def validate_user_name(self, value):
        if not value.isalnum():
            raise serializers.ValidationError("Только латинские буквы и цифры.")
        return value

    def validate_text(self, value):
        return bleach.clean(value, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

    def create(self, validated_data):
        files = validated_data.pop('files', [])
        comment = Comment.objects.create(**validated_data)

        for file in files:
            processed_file = resize_image_if_needed(file)
            CommentFile.objects.create(comment=comment, file=processed_file)

        return comment
