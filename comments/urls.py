from captcha.views import captcha_refresh
from django.urls import path
from .views import CommentListView

app_name = 'comments'


urlpatterns = [

    path('', CommentListView.as_view(), name='index'),
    path('captcha/refresh/', captcha_refresh, name='captcha-refresh'),
]