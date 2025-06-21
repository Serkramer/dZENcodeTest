from captcha.views import captcha_refresh
from django.urls import path
from .views import CommentListView, LoadCommentFormView

app_name = 'comments'

urlpatterns = [

    path('', CommentListView.as_view(), name='index'),
    path('captcha/refresh/', captcha_refresh, name='captcha-refresh'),
    path('load_form/', LoadCommentFormView.as_view(), name='load_comment_form'),

]
