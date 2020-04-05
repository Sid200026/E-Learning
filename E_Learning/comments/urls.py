from django.urls import path, re_path
from .views import CommentList, CommentDetail, ReplyList, ReplyDetail

app_name = "comments"

urlpatterns = [
    path(
        "main/<int:course_id>/<int:pk>", CommentDetail.as_view(), name="comment-detail"
    ),
    path("main/<int:course_id>/", CommentList.as_view(), name="comment-list"),
    path(
        "reply/<int:course_id>/<int:comment_id>/<int:pk>/",
        ReplyDetail.as_view(),
        name="reply-detail",
    ),
    path(
        "reply/<int:course_id>/<int:comment_id>/",
        ReplyList.as_view(),
        name="reply-list",
    ),
]
