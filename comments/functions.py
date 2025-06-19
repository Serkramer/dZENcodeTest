import sys
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


def resize_image_if_needed(uploaded_file):
    ext = uploaded_file.name.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'gif']:
        return uploaded_file  # Ничего не делаем для .txt

    try:
        image = Image.open(uploaded_file)
        if image.width <= 320 and image.height <= 240:
            return uploaded_file  # Уже маленькое — не изменяем

        image.thumbnail((320, 240), Image.ANTIALIAS)  # Уменьшение

        output = BytesIO()
        image_format = 'JPEG' if ext in ['jpg', 'jpeg'] else ext.upper()
        image.save(output, format=image_format)
        output.seek(0)

        new_file = InMemoryUploadedFile(
            output,
            uploaded_file.field_name,
            uploaded_file.name,
            uploaded_file.content_type,
            sys.getsizeof(output),
            uploaded_file.charset
        )
        return new_file
    except Exception as e:
        return uploaded_file