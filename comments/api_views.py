from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from drf_spectacular.utils import (
    extend_schema, OpenApiExample, OpenApiResponse, OpenApiParameter, OpenApiRequest
)
from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, filters, mixins
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView

from comments.models import Comment
from comments.serializers import CommentSerializer, CreateCommentSerializer
from rest_framework.parsers import MultiPartParser, FormParser

class CommentPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
from rest_framework.permissions import IsAuthenticated


class CommentViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):

    queryset = Comment.objects.filter(parent__isnull=True).order_by('-created_at')
    pagination_class = CommentPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, DjangoFilterBackend]
    ordering_fields = ['user_name', 'email', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCommentSerializer
        return CommentSerializer

    @extend_schema(
        summary="Получить список комментариев",
        description="Возвращает верхнеуровневые комментарии с вложенными ответами и файлами.",
        tags=["Комментарии"],
        parameters=[
            OpenApiParameter(name='ordering', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY,
                             description='Сортировка: user_name, email, created_at (например, -created_at)'),
            OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                             description='Номер страницы'),
            OpenApiParameter(name='page_size', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY,
                             description='Количество записей на странице')
        ],
        responses=CommentSerializer
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Создать комментарий",
        description="Создаёт комментарий с файлами (JPG, PNG, GIF, TXT). Поддерживает вложенность через `parent`. "
                    "Формат запроса должен быть multipart/form-data.",
        tags=["Комментарии"],
        request=CreateCommentSerializer,
        responses={
            201: OpenApiResponse(response=CommentSerializer, description="Комментарий создан"),
            400: OpenApiResponse(description="Ошибка валидации")
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class CaptchaAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        captcha = CaptchaStore.generate_key()
        image_url = captcha_image_url(captcha)

        return Response({
            "captcha_key": captcha,
            "image_url": request.build_absolute_uri(image_url)
        })