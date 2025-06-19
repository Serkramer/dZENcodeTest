from django.core.validators import RegexValidator, FileExtensionValidator
from django.db import models
from django.utils.timezone import now
# Create your models here.


class Comment(models.Model):
    user_name = models.CharField(max_length=255,
                                 validators=[RegexValidator(r'^[a-zA-Z0-9]+$',
                                                            'Разрешены только цифры и буквы латинского алфавита.')],
                                 verbose_name='User name'
                                 )
    email = models.EmailField(verbose_name="Email")
    home_page = models.URLField(blank=True, null=True, verbose_name="Home page")
    text = models.TextField(verbose_name="Text")
    created_at = models.DateTimeField(default=now)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        blank=True,
        null=True,
        verbose_name="Parent Comment"
    )

    def __str__(self):
        return f"{self.user_name} - {self.created_at:%Y-%m-%d %H:%M}"


def user_file_path(instance, filename):
    return f'comment_files/{instance.comment.id}/{filename}'


class CommentFile(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(
        upload_to=user_file_path,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'txt'])
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def is_image(self):
        return self.file.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))

    def is_text(self):
        return self.file.name.lower().endswith('.txt')

