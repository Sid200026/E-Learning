from django.urls import path, re_path
from .views import CommentList, CommentDetail, ReplyList, ReplyDetail

app_name = "comments"

urlpatterns = [
    path("main/<int:pk>", CommentDetail.as_view(), name="comment-detail"),
    path("main/", CommentList.as_view(), name="comment-list"),
    path("reply/<int:pk>/", ReplyDetail.as_view(), name="reply-detail"),
    path("reply/all/<int:comment_id>/", ReplyList.as_view(), name="reply-list"),
]
