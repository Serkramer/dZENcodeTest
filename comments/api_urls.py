from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from comments.api_views import CommentViewSet, CaptchaAPIView

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')


urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('captcha/', CaptchaAPIView.as_view(), name='api_captcha'),
]

urlpatterns += router.urls