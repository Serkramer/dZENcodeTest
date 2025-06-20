import sys
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile



def resize_image_if_needed(uploaded_file):
    ext = uploaded_file.name.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'gif']:
        return uploaded_file  # Текст — не обрабатываем

    try:
        # Считываем содержимое в память
        image_data = uploaded_file.read()
        image = Image.open(BytesIO(image_data))
        image.load()  # Полная загрузка

        # Если изображение уже маленькое — не обрезаем
        if image.width <= 320 and image.height <= 240:
            uploaded_file.seek(0)
            return uploaded_file

        # Масштабирование
        image.thumbnail((320, 240), Image.Resampling.LANCZOS)

        # Сохраняем уменьшенное изображение
        output = BytesIO()
        image_format = 'JPEG' if ext in ['jpg', 'jpeg'] else ext.upper()
        image.save(output, format=image_format)
        output.seek(0)

        return InMemoryUploadedFile(
            file=output,
            field_name='file',
            name=uploaded_file.name,
            content_type=uploaded_file.content_type,
            size=output.getbuffer().nbytes,
            charset=None
        )
    except Exception as e:
        uploaded_file.seek(0)
        return uploaded_file