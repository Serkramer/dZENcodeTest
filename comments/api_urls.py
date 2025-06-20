from rest_framework.routers import DefaultRouter

from comments.api_views import CommentViewSet

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = router.urls